import assert from 'node:assert/strict'
import test from 'node:test'
import { extractStreamingAnswer } from './streamingJson.js'

test('在完整 JSON 到达前，逐字符显示回答并解码换行、引号和反斜线', () => {
  const answer = '你好\n代码："SSE"，路径 C:\\demo\t完成'
  const json = JSON.stringify({ answer })
  let previous = ''
  for (let end = 0; end <= json.length; end += 1) {
    const partial = extractStreamingAnswer(json.slice(0, end))
    assert.ok(answer.startsWith(partial), `${end}: ${partial}`)
    assert.ok(partial.startsWith(previous))
    previous = partial
  }
  assert.equal(previous, answer)
  assert.equal(extractStreamingAnswer('{"answer":"尚未完成'), '尚未完成')
})

test('等待跨片段的 Unicode 转义和代理对，避免显示半个字符', () => {
  assert.equal(extractStreamingAnswer(String.raw`{"answer":"你好\u4e`), '你好')
  assert.equal(extractStreamingAnswer(String.raw`{"answer":"你好\u4e16`), '你好世')
  assert.equal(extractStreamingAnswer(String.raw`{"answer":"Hi\ud83d`), 'Hi')
  assert.equal(extractStreamingAnswer(String.raw`{"answer":"Hi\ud83d\ude`), 'Hi')
  assert.equal(extractStreamingAnswer(String.raw`{"answer":"Hi\ud83d\ude00`), 'Hi😀')
})

test('只读取顶层 answer，不把字符串内容或嵌套字段当成回答', () => {
  const prefix = JSON.stringify({ note: '"answer":"假回答"', nested: { answer: '嵌套回答' } }).slice(0, -1)
  assert.equal(extractStreamingAnswer(`${prefix},"answer":"真正的回答`), '真正的回答')
  assert.equal(extractStreamingAnswer('{"nested":{"answer":"嵌套"}}'), '')
  assert.equal(extractStreamingAnswer('{"answer":42}'), '')
  assert.equal(extractStreamingAnswer('不合法 JSON'), '')
})
