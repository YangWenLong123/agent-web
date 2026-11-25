import assert from 'node:assert/strict'
import test from 'node:test'
import { createRenderer } from 'vue'
import { useSseStream } from './useSseStream.js'

function setup(t) {
  const connections = []
  const posts = []
  const timers = new Map()
  let now = 0
  let timerId = 0
  let stream
  class FakeEventSource {
    constructor(url) {
      this.url = new URL(url, 'http://localhost')
      this.handlers = {}
      this.closed = false
      connections.push(this)
    }
    addEventListener(event, callback) { this.handlers[event] = callback }
    close() { this.closed = true }
    message(index, content) {
      this.onmessage({ lastEventId: String(index), data: JSON.stringify({ type: 'delta', index, content }) })
    }
    done(count, result) {
      this.handlers.done({ lastEventId: String(count + 1), data: JSON.stringify({ type: 'done', count, result, usage: { total_tokens: 20 } }) })
    }
  }
  const old = { window: globalThis.window, EventSource: globalThis.EventSource, fetch: globalThis.fetch }
  globalThis.EventSource = FakeEventSource
  globalThis.window = {
    setInterval(callback) { timers.set(++timerId, callback); return timerId },
    clearInterval(id) { timers.delete(id) },
  }
  globalThis.fetch = async (url, options) => {
    if (!options) return { ok: true, json: async () => [] }
    posts.push({ url, options })
    return { ok: true, json: async () => ({
      stream_id: 'a'.repeat(32), model: 'deepseek-v4-pro',
      conversation_id: 'b'.repeat(32), turn_id: String(posts.length).padStart(32, '0'),
      title: '测试对话', context_count: posts.length - 1,
    }) }
  }
  t.mock.method(performance, 'now', () => now)
  const renderer = createRenderer({ createComment: () => ({}), insert() {}, remove() {}, parentNode: () => null, nextSibling: () => null })
  const app = renderer.createApp({ setup() { stream = useSseStream(); return () => null } })
  app.mount({})
  t.after(() => {
    app.unmount()
    for (const key of Object.keys(old)) {
      if (old[key] === undefined) delete globalThis[key]
      else globalThis[key] = old[key]
    }
  })
  return { stream, connections, posts, timers, advance(seconds) {
    now += seconds * 1000
    for (const callback of timers.values()) callback()
  } }
}

test('POST 提交内容，SSE 拼接片段并接收完整 JSON', async (t) => {
  const { stream, connections, posts, timers } = setup(t)
  await stream.start('  你好  ')
  assert.equal(posts[0].url, '/api/sse/generations')
  assert.deepEqual(JSON.parse(posts[0].options.body), { content: '你好' })
  assert.equal(stream.submittedContent.value, '你好')
  assert.equal(posts[0].options.method, 'POST')
  connections[0].message(1, '{"answer":')
  connections[0].message(2, '"你好"}')
  assert.equal(stream.rawJson.value, '{"answer":"你好"}')
  connections[0].done(2, { answer: '你好' })
  assert.deepEqual(stream.result.value, { answer: '你好' })
  assert.equal(stream.status.value, 'completed')
  assert.equal(stream.usage.value.total_tokens, 20)
  assert.equal(connections[0].closed, true)
  assert.equal(timers.size, 0)
})

test('停止后沿用任务 ID 续传，不再次调用模型；计时排除暂停', async (t) => {
  const { stream, connections, posts, advance } = setup(t)
  await stream.start('介绍 SSE')
  const first = connections[0]
  first.message(1, '{"answer":')
  advance(2)
  stream.stop()
  advance(20)
  assert.equal(stream.canResume.value, true)
  assert.equal(stream.elapsed.value, 2)
  stream.resume()
  const resumed = connections[1]
  assert.equal(resumed.url.searchParams.get('stream_id'), 'a'.repeat(32))
  assert.equal(resumed.url.searchParams.get('after_id'), '1')
  assert.equal(posts.length, 1)
  assert.equal(stream.submittedContent.value, '介绍 SSE')
  first.message(2, '旧数据')
  first.onerror()
  assert.equal(stream.records.value.length, 1)
  resumed.message(2, '"SSE"}')
  advance(0.5)
  resumed.done(2, { answer: 'SSE' })
  assert.equal(stream.elapsed.value, 2.5)
  assert.equal(stream.status.value, 'completed')
  assert.equal(stream.rawJson.value, '{"answer":"SSE"}')
})

test('上游错误保留片段，清空后重置任务和结果', async (t) => {
  const { stream, connections, timers } = setup(t)
  await stream.start('你好')
  connections[0].message(1, '{')
  connections[0].handlers.failure({ lastEventId: '2', data: JSON.stringify({ type: 'error', message: '账户余额不足' }) })
  assert.equal(stream.error.value, '账户余额不足')
  assert.equal(stream.records.value.length, 1)
  assert.equal(stream.status.value, 'error')
  assert.equal(timers.size, 0)
  stream.clear()
  assert.equal(stream.streamId.value, '')
  assert.equal(stream.submittedContent.value, '')
  assert.equal(stream.rawJson.value, '')
  assert.equal(stream.result.value, null)
  assert.equal(stream.status.value, 'idle')
})

test('拒绝空输入、错误事件序号及不完整 done', async (t) => {
  const { stream, connections, posts } = setup(t)
  await stream.start('  ')
  assert.equal(posts.length, 0)
  await stream.start('你好')
  connections[0].message(2, '跳号')
  assert.equal(stream.status.value, 'error')
  await stream.start('你好')
  connections[1].done(1, { answer: '不完整' })
  assert.equal(stream.status.value, 'error')
})

test('POST 返回前停止，迟到响应不能创建订阅', async (t) => {
  const { stream, connections } = setup(t)
  let resolve
  globalThis.fetch = () => new Promise((done) => { resolve = done })
  const pending = stream.start('你好')
  stream.stop()
  resolve({ ok: true, json: async () => ({ stream_id: 'a'.repeat(32), model: 'deepseek-v4-pro' }) })
  await pending
  assert.equal(connections.length, 0)
  assert.equal(stream.status.value, 'stopped')
  assert.equal(stream.canResume.value, false)
})

test('POST 错误展示后端提示，首条数据前也可以续传', async (t) => {
  const { stream, connections } = setup(t)
  const fetchSuccess = globalThis.fetch
  globalThis.fetch = async () => ({ ok: false, json: async () => ({ detail: '后端未配置密钥' }) })
  await stream.start('你好')
  assert.equal(stream.error.value, '后端未配置密钥')
  globalThis.fetch = fetchSuccess
  await stream.start('你好')
  stream.stop()
  stream.resume()
  assert.equal(connections.at(-1).url.searchParams.get('after_id'), '0')
})

test('下一轮追加问答并传入同一对话 ID，新建后不丢失已保存的会话标识', async (t) => {
  const { stream, connections, posts } = setup(t)
  await stream.start('我的项目叫流星')
  connections[0].message(1, '{"answer":"已记住"}')
  connections[0].done(1, { answer: '已记住' })
  await stream.start('项目叫什么？')
  assert.equal(stream.turns.value.length, 2)
  assert.equal(stream.turns.value[0].answer, '已记住')
  assert.deepEqual(JSON.parse(posts[1].options.body), { content: '项目叫什么？', conversation_id: 'b'.repeat(32) })
  connections[1].message(1, '{"answer":"流星"}')
  connections[1].done(1, { answer: '流星' })
  assert.deepEqual(stream.turns.value.map((turn) => turn.content), ['我的项目叫流星', '项目叫什么？'])
  stream.clear()
  assert.equal(stream.conversationId.value, '')
  assert.equal(stream.turns.value.length, 0)
  await stream.start('另一段对话')
  assert.equal(JSON.parse(posts[2].options.body).conversation_id, undefined)
})

test('刷新初始化恢复历史问答，再次发送继续使用原对话', async (t) => {
  const { stream, connections, posts } = setup(t)
  const normalFetch = globalThis.fetch
  const id = 'c'.repeat(32)
  globalThis.fetch = async (url, options) => {
    if (options) return normalFetch(url, options)
    if (url === '/api/sse/conversations') return { ok: true, json: async () => [{ id, title: '已保存的问答', turn_count: 1 }] }
    return { ok: true, json: async () => ({ id, turns: [{
      id: 'd'.repeat(32), content: '请记住蓝色', answer: '好的', raw_json: '{"answer":"好的"}',
      status: 'completed', result: { answer: '好的' }, model: 'deepseek-v4-pro', stream_id: 'e'.repeat(32), usage: null,
    }] }) }
  }
  await stream.initialize()
  assert.equal(stream.conversationId.value, id)
  assert.equal(stream.turns.value[0].answer, '好的')
  assert.equal(stream.result.value.answer, '好的')
  assert.equal(connections.length, 0)
  await stream.start('是什么颜色？')
  assert.equal(JSON.parse(posts[0].options.body).conversation_id, id)
  assert.equal(stream.turns.value.length, 2)
})

test('刷新时任务仍在生成，从事件零重放并接续回答，不创建新任务', async (t) => {
  const { stream, connections, posts } = setup(t)
  const id = 'c'.repeat(32)
  globalThis.fetch = async (url) => ({ ok: true, json: async () => (
    url === '/api/sse/conversations' ? [{ id, title: '生成中的对话', turn_count: 1 }] : { id, turns: [{
      id: 'd'.repeat(32), content: '请介绍 SSE', answer: '', raw_json: '{"answer":"已保存的部分',
      status: 'generating', result: null, model: 'deepseek-v4-pro', stream_id: 'e'.repeat(32), usage: null,
    }] }
  ) })
  await stream.initialize()
  assert.equal(posts.length, 0)
  assert.equal(connections[0].url.searchParams.get('after_id'), '0')
  assert.equal(connections[0].url.searchParams.get('stream_id'), 'e'.repeat(32))
  connections[0].message(1, '{"answer":"完整回答"}')
  connections[0].done(1, { answer: '完整回答' })
  assert.equal(stream.turns.value[0].answer, '完整回答')
  assert.equal(stream.turns.value[0].raw_json, '{"answer":"完整回答"}')
  assert.equal(stream.turns.value.length, 1)
})
