import { computed, onBeforeUnmount, ref } from 'vue'

export function useSseStream() {
  const records = ref([])
  const status = ref('idle')
  const error = ref('')
  const elapsed = ref(0)
  const submittedContent = ref('')
  const turns = ref([])
  const conversations = ref([])
  const conversationId = ref('')
  const activeTurnId = ref('')
  const historyLoading = ref(false)
  const historyError = ref('')
  const streamId = ref('')
  const model = ref('deepseek-v4-pro')
  const result = ref(null)
  const usage = ref(null)
  const lastEventId = ref(0)
  const requestUrl = ref('')
  const isActive = computed(() => ['connecting', 'streaming'].includes(status.value))
  const canResume = computed(() => status.value === 'stopped' && Boolean(streamId.value))
  const rawJson = computed(() => records.value.map(({ data }) => data.content).join(''))
  let source = null
  let controller = null
  let timer = null
  let startedAt = 0
  let elapsedBeforeConnection = 0
  let version = 0

  function currentTurn() {
    return turns.value.find((turn) => turn.id === activeTurnId.value)
  }

  function rememberConversation(id) {
    try {
      if (id) window.localStorage?.setItem('deepseek-conversation-id', id)
      else window.localStorage?.removeItem('deepseek-conversation-id')
    } catch { /* 浏览器禁用本地存储时仍可通过历史列表恢复。 */ }
  }

  async function readResponse(response) {
    const body = await response.json()
    if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : '请求失败，请稍后重试。')
    return body
  }

  async function refreshConversations() {
    try {
      const list = await readResponse(await fetch('/api/sse/conversations'))
      if (!Array.isArray(list)) throw new Error('历史对话数据异常。')
      conversations.value = list
      historyError.value = ''
    } catch {
      historyError.value = '历史列表暂时无法读取，请刷新重试。'
    }
  }

  function updateElapsed() {
    elapsed.value = elapsedBeforeConnection + (performance.now() - startedAt) / 1000
  }

  function disconnect() {
    source?.close()
    source = null
    controller?.abort()
    controller = null
    window.clearInterval(timer)
    timer = null
  }

  function finish(nextStatus) {
    updateElapsed()
    version += 1
    disconnect()
    status.value = nextStatus
  }

  function fail(message) {
    error.value = message
    const turn = currentTurn()
    if (turn) { turn.status = 'error'; turn.error = message }
    finish('error')
  }

  function begin() {
    disconnect()
    error.value = ''
    status.value = 'connecting'
    elapsedBeforeConnection = elapsed.value
    startedAt = performance.now()
    timer = window.setInterval(updateElapsed, 100)
  }

  function connect(ticket) {
    try {
      const query = new URLSearchParams({ stream_id: streamId.value, after_id: String(lastEventId.value) })
      requestUrl.value = `/api/sse/jsonlines?${query}`
      const connection = new EventSource(requestUrl.value)
      source = connection
      const isCurrent = () => ticket === version && source === connection
      const readEvent = (event) => {
        const id = Number(event.lastEventId)
        if (!Number.isInteger(id) || id !== lastEventId.value + 1) throw new Error('Invalid event ID')
        const data = JSON.parse(event.data)
        if (!data || typeof data !== 'object') throw new Error('Invalid data')
        return { id, data }
      }

      connection.onopen = () => {
        if (isCurrent()) status.value = 'streaming'
      }
      connection.onmessage = (event) => {
        if (!isCurrent()) return
        try {
          const { id, data } = readEvent(event)
          if (data.type !== 'delta' || data.index !== records.value.length + 1 || typeof data.content !== 'string') {
            throw new Error('Invalid delta')
          }
          records.value.push({ data, receivedAt: new Date() })
          const turn = currentTurn()
          if (turn) turn.raw_json += data.content
          lastEventId.value = id
        } catch {
          fail('收到的数据格式异常，请重新发送。已有内容已保留。')
        }
      }
      connection.addEventListener('done', (event) => {
        if (!isCurrent()) return
        try {
          const { id, data } = readEvent(event)
          if (
            data.type !== 'done' || data.count !== records.value.length ||
            !data.result || typeof data.result !== 'object' || Array.isArray(data.result) ||
            typeof data.result.answer !== 'string'
          ) throw new Error('Invalid result')
          result.value = data.result
          usage.value = data.usage ?? null
          lastEventId.value = id
          const turn = currentTurn()
          if (turn) Object.assign(turn, { status: 'completed', answer: data.result.answer, result: data.result, usage: data.usage ?? null })
          finish('completed')
          void refreshConversations()
        } catch {
          fail('模型结果不完整或格式异常，请重新发送。')
        }
      })
      connection.addEventListener('failure', (event) => {
        if (!isCurrent()) return
        try {
          const { id, data } = readEvent(event)
          if (data.type !== 'error' || typeof data.message !== 'string') throw new Error('Invalid error')
          lastEventId.value = id
          fail(data.message)
        } catch {
          fail('生成失败，请重新发送。')
        }
      })
      connection.onerror = () => {
        if (isCurrent()) fail('连接中断或记录已过期，请重新发送。已有内容已保留。')
      }
    } catch {
      fail('无法建立实时连接，请检查浏览器和服务状态。')
    }
  }

  async function start(content) {
    if (isActive.value || historyLoading.value) return
    if (canResume.value) {
      error.value = '请先继续接收本轮回答，完成后再发送下一条，或新建对话。'
      return
    }
    const text = typeof content === 'string' ? content.trim() : ''
    if (!text || text.length > 8000) {
      error.value = '请输入 1–8000 个字符的内容。'
      return
    }
    const ticket = ++version
    submittedContent.value = text
    const pendingId = `pending-${ticket}`
    turns.value.push({ id: pendingId, content: text, answer: '', raw_json: '', status: 'generating', model: model.value, error: '' })
    activeTurnId.value = pendingId
    records.value = []
    elapsed.value = 0
    streamId.value = ''
    lastEventId.value = 0
    requestUrl.value = ''
    result.value = null
    usage.value = null
    begin()
    controller = new AbortController()
    try {
      const response = await fetch('/api/sse/generations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: text, ...(conversationId.value ? { conversation_id: conversationId.value } : {}) }),
        signal: controller.signal,
      })
      const body = await response.json()
      if (ticket !== version) return
      if (!response.ok) {
        throw new Error(typeof body.detail === 'string' ? body.detail : '提交失败，请检查输入或稍后重试。')
      }
      if (!/^[a-f0-9]{32}$/.test(body.stream_id) || typeof body.model !== 'string') {
        throw new Error('服务返回的任务信息异常。')
      }
      if (!/^[a-f0-9]{32}$/.test(body.conversation_id) || !/^[a-f0-9]{32}$/.test(body.turn_id)) {
        throw new Error('服务返回的对话信息异常。')
      }
      const turn = currentTurn()
      if (turn) Object.assign(turn, { id: body.turn_id, stream_id: body.stream_id, model: body.model, context_count: body.context_count })
      activeTurnId.value = body.turn_id
      conversationId.value = body.conversation_id
      rememberConversation(body.conversation_id)
      streamId.value = body.stream_id
      model.value = body.model
      connect(ticket)
      void refreshConversations()
    } catch (err) {
      if (ticket === version) fail(err instanceof Error ? err.message : '提交失败，请稍后重试。')
    }
  }

  function resume() {
    if (!canResume.value) return
    const ticket = ++version
    begin()
    connect(ticket)
  }

  function stop() {
    if (isActive.value) finish('stopped')
  }

  function resetCurrent() {
    records.value = []
    error.value = ''
    submittedContent.value = ''
    activeTurnId.value = ''
    elapsed.value = 0
    streamId.value = ''
    lastEventId.value = 0
    requestUrl.value = ''
    result.value = null
    usage.value = null
    status.value = 'idle'
  }

  async function selectConversation(id) {
    if (isActive.value || historyLoading.value || !id) return
    const ticket = ++version
    historyLoading.value = true
    disconnect()
    try {
      const body = await readResponse(await fetch(`/api/sse/conversations/${id}`))
      if (ticket !== version) return
      if (!Array.isArray(body.turns)) throw new Error('对话数据异常。')
      resetCurrent()
      conversationId.value = body.id
      turns.value = body.turns
      rememberConversation(body.id)
      const latest = turns.value.at(-1)
      if (latest) {
        activeTurnId.value = latest.id
        submittedContent.value = latest.content
        streamId.value = latest.stream_id
        model.value = latest.model
        result.value = latest.result
        usage.value = latest.usage
        status.value = latest.status === 'completed' ? 'completed' : 'error'
        error.value = latest.error || ''
        if (latest.status === 'generating') {
          latest.raw_json = ''
          begin()
          connect(ticket)
        }
      }
    } catch (err) {
      if (ticket === version) error.value = err instanceof Error ? err.message : '读取对话失败。'
    } finally {
      historyLoading.value = false
    }
  }

  async function initialize() {
    if (isActive.value || historyLoading.value) return
    historyLoading.value = true
    await refreshConversations()
    historyLoading.value = false
    let remembered = ''
    try { remembered = window.localStorage?.getItem('deepseek-conversation-id') || '' } catch { /* 使用最近对话。 */ }
    const target = conversations.value.find(({ id }) => id === remembered) || conversations.value[0]
    if (target) await selectConversation(target.id)
  }

  function clear() {
    if (isActive.value || historyLoading.value) return
    version += 1
    disconnect()
    resetCurrent()
    turns.value = []
    conversationId.value = ''
    rememberConversation('')
  }

  onBeforeUnmount(() => { version += 1; disconnect() })
  return {
    records, status, error, elapsed, submittedContent, streamId, model, result, usage, rawJson,
    turns, conversations, conversationId, activeTurnId, historyLoading, historyError,
    initialize, selectConversation,
    requestUrl, isActive, canResume, start, resume, stop, clear,
  }
}
