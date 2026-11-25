<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useSseStream } from './composables/useSseStream'
import { extractStreamingAnswer } from './utils/streamingJson'

const content = ref('请用三句话介绍 SSE 的用途。')
const view = ref('chat')
const autoScroll = ref(true)
const logElement = ref(null)
const {
  records, status, error, elapsed, model, result, usage, rawJson,
  turns, conversations, conversationId, activeTurnId, historyLoading, historyError,
  initialize, selectConversation,
  requestUrl, isActive, canResume, start, resume, stop, clear,
} = useSseStream()

const statusLabel = computed(() => ({
  idle: '待连接',
  connecting: '连接中',
  streaming: '接收中',
  completed: '已完成',
  stopped: '已停止',
  error: '连接异常',
})[status.value])
const endpoint = computed(() => requestUrl.value || '/api/sse/generations')
const resultJson = computed(() => result.value ? JSON.stringify(result.value, null, 2) : rawJson.value)
const isBusy = computed(() => isActive.value || historyLoading.value)
function answerFor(turn) {
  return turn.result?.answer ?? (turn.answer || extractStreamingAnswer(turn.raw_json || ''))
}
function stateFor(turn) {
  return turn.id === activeTurnId.value ? status.value : turn.status
}
function placeholderFor(turn) {
  if (stateFor(turn) === 'completed') return '模型返回了空回答，可以继续追问。'
  if (['error', 'interrupted'].includes(stateFor(turn))) return turn.error || '回答中断，可以发送新问题。'
  if (stateFor(turn) === 'stopped') return '已停止接收，点击「继续接收」查看后续回答。'
  return '正在思考你的问题，请稍候…'
}
function switchConversation(id) {
  if (id) void selectConversation(id)
  else clear()
}
const resultText = computed(() => ({
  idle: '输入内容后发送给模型',
  connecting: '正在提交内容并建立连接…',
  streaming: '正在接收模型输出…',
  completed: records.value.length ? `已接收 ${records.value.length} 个片段，完整 JSON 已返回` : '已恢复保存的历史回答',
  stopped: canResume.value ? `已停止，保留 ${records.value.length} 个片段，可继续接收` : '提交已停止，可以重新发送',
  error: '生成已中断，可重新发送',
})[status.value])

function formatTime(date) {
  return `${date.toLocaleTimeString('zh-CN', { hour12: false })}.${String(date.getMilliseconds()).padStart(3, '0')}`
}

async function scrollToLatest() {
  if (!autoScroll.value) return
  await nextTick()
  const element = logElement.value
  if (element) element.scrollTop = element.scrollHeight
}

watch(() => records.value.length, scrollToLatest)
watch(autoScroll, scrollToLatest)
watch(view, scrollToLatest)
watch(result, scrollToLatest)
watch(() => turns.value.length, scrollToLatest)
onMounted(initialize)
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <a class="brand" href="/" aria-label="SSE 实时数据首页">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="m5 7 5 5-5 5M13 17h6" />
          </svg>
        </span>
        <span>Stream <span class="brand-light">/ 数据流</span></span>
      </a>
      <a class="docs-link" href="/docs" target="_blank" rel="noopener noreferrer">
        API 文档 <span aria-hidden="true">↗</span>
      </a>
    </header>

    <main>
      <div class="page-heading">
        <div>
          <p class="eyebrow">DEEPSEEK · STREAMING JSON</p>
          <h1>与模型实时对话</h1>
          <p class="page-description">实时对话，自动保存记录，让模型记住之前的问答。</p>
        </div>
        <span class="status-badge" :class="status" role="status">
          <span class="status-dot" aria-hidden="true"></span>{{ statusLabel }}
        </span>
      </div>

      <div class="workspace">
        <aside class="settings-panel" aria-labelledby="settings-title">
          <div class="section-heading">
            <h2 id="settings-title">发送内容</h2>
            <span class="section-caption">{{ model }}</span>
          </div>

          <div class="field history-selection">
            <label for="conversation">历史对话</label>
            <select id="conversation" :value="conversationId" :disabled="isBusy" @change="switchConversation($event.target.value)">
              <option value="">新对话</option>
              <option v-for="conversation in conversations" :key="conversation.id" :value="conversation.id">{{ conversation.title }}（{{ conversation.turn_count }} 轮）</option>
            </select>
            <p v-if="historyLoading" class="field-hint">正在恢复对话…</p>
            <p v-else class="field-hint">问答自动保存，可随时切换回来</p>
            <p v-if="historyError" class="history-error" role="alert">{{ historyError }}</p>
          </div>

          <form @submit.prevent="start(content)">
            <div class="field">
              <label for="content">你的问题</label>
              <textarea id="content" v-model="content" rows="8" maxlength="8000" required :disabled="isBusy" aria-describedby="content-hint" placeholder="输入问题，或接着上一轮继续追问…"></textarea>
              <p id="content-hint" class="field-hint">{{ content.length }} / 8000 字符 · 对话记忆已开启</p>
            </div>

            <button class="button button-primary" type="submit" :disabled="isBusy || canResume">
              <span v-if="isActive" class="spinner" aria-hidden="true"></span>
              <svg v-else viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M6 3.5a.75.75 0 0 1 1.14-.64l10 6a.75.75 0 0 1 0 1.28l-10 6A.75.75 0 0 1 6 15.5z" /></svg>
              {{ historyLoading ? '正在恢复…' : (isActive ? '正在生成…' : '发送消息') }}
            </button>

            <div class="secondary-actions">
              <button v-if="canResume" class="button button-secondary" type="button" :disabled="historyLoading" @click="resume">
                <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M6 3.5a.75.75 0 0 1 1.14-.64l10 6a.75.75 0 0 1 0 1.28l-10 6A.75.75 0 0 1 6 15.5z" /></svg>
                继续接收
              </button>
              <button v-else class="button button-secondary" type="button" :disabled="!isActive" @click="stop">
                <span class="stop-icon" aria-hidden="true"></span>停止接收
              </button>
              <button class="button button-secondary" type="button" :disabled="isBusy" @click="clear">
                新建对话
              </button>
            </div>
          </form>

          <p v-if="error" class="error-message" role="alert">{{ error }}</p>

          <div class="connection-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p>每条消息都会保存，模型会参考当前对话最近的完整问答。停止后请先继续接收，再发送下一条；新建对话会保留历史记录。</p>
          </div>
        </aside>

        <section class="stream-panel" aria-labelledby="records-title">
          <div class="stream-heading">
            <div class="records-title">
              <h2 id="records-title">对话与结果</h2>
              <span class="format-label">JSON + SSE</span>
            </div>
            <label class="auto-scroll"><input v-model="autoScroll" type="checkbox" />自动滚动</label>
          </div>

          <div class="stream-stats">
            <span>已接收 <strong>{{ records.length }}</strong> 个片段<span v-if="usage?.total_tokens" class="token-total"> · {{ usage.total_tokens }} tokens</span></span>
            <span>耗时 <strong class="elapsed">{{ elapsed.toFixed(1) }}</strong> 秒</span>
          </div>
          <div class="view-tabs" aria-label="结果视图">
            <button type="button" :aria-pressed="view === 'chat'" @click="view = 'chat'">内容对话</button>
            <button type="button" :aria-pressed="view === 'result'" @click="view = 'result'">{{ result ? '完整 JSON' : '实时输出' }}</button>
            <button type="button" :aria-pressed="view === 'events'" @click="view = 'events'">JSON 事件</button>
          </div>
          <div class="progress-track" :class="{ 'is-streaming': isActive }" aria-hidden="true">
            <div class="progress-fill" :style="{ width: status === 'completed' ? '100%' : (isActive ? '40%' : '0%') }"></div>
          </div>

          <div ref="logElement" class="log-view" :class="{ 'conversation-view': view === 'chat' }" role="log" :aria-label="view === 'chat' ? '我的问题与实时回答' : '实时接收的 JSON 数据'" aria-live="polite" aria-relevant="additions text" tabindex="0">
            <div v-if="view === 'chat'" class="conversation">
              <div v-if="turns.length" class="memory-banner"><span>记忆已开启</span><span>{{ turns.length }} 轮问答 · 自动保存</span></div>
              <div v-if="!turns.length" class="conversation-empty">
                <svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M8 6h16a4 4 0 0 1 4 4v10a4 4 0 0 1-4 4H14l-6 4v-4a4 4 0 0 1-4-4V10a4 4 0 0 1 4-4Z" /><path d="M10 12h12M10 17h8" /></svg>
                <h3>你的问题，实时的回答</h3>
                <p>在左侧输入内容并发送，对话会显示在这里。</p>
              </div>
              <div v-for="turn in turns" v-else :key="turn.id" class="conversation-turn">
                <article class="chat-message user-message" aria-label="我的问题">
                  <div class="message-heading"><span>我的问题</span><span class="chat-avatar user-avatar" aria-hidden="true">我</span></div>
                  <div class="chat-bubble user-bubble">{{ turn.content }}</div>
                </article>
                <article class="chat-message assistant-message" aria-label="模型实时回答">
                  <div class="message-heading"><span class="chat-avatar assistant-avatar" aria-hidden="true">AI</span><span>{{ turn.model }}</span><span v-if="['connecting', 'streaming', 'generating'].includes(stateFor(turn))" class="reply-status">正在回答</span></div>
                  <div class="chat-bubble assistant-bubble">
                    <p v-if="answerFor(turn)" class="answer-text">{{ answerFor(turn) }}<span v-if="turn.id === activeTurnId && isActive" class="typing-caret" aria-hidden="true"></span></p>
                    <p v-else class="answer-placeholder">{{ placeholderFor(turn) }}</p>
                  </div>
                  <p v-if="answerFor(turn) && stateFor(turn) === 'stopped'" class="reply-note">接收已暂停，继续后会接着显示。</p>
                  <p v-if="answerFor(turn) && ['error', 'interrupted'].includes(stateFor(turn))" class="reply-note">回答中断，已保留收到的内容。</p>
                  <p v-if="turn.context_count" class="reply-note">本次回答参考了 {{ turn.context_count }} 轮历史问答。</p>
                </article>
              </div>
            </div>
            <pre v-else-if="view === 'result' && (result || rawJson)" class="model-output">{{ resultJson }}</pre>
            <div v-else-if="!records.length" class="empty-state">
              <span class="empty-icon" :class="{ listening: isActive }" aria-hidden="true">
                <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                  <rect x="8" y="10" width="32" height="28" rx="5" /><path d="m16 20 5 4-5 4M26 28h6" />
                </svg>
              </span>
              <h3>{{ isActive ? '等待模型响应' : '暂无本轮事件' }}</h3>
              <p>{{ isActive ? '模型正在处理，结果将在此实时显示。' : '历史回答可在「内容对话」中查看，发送消息后会显示新事件。' }}</p>
              <span class="empty-example">{ "answer": "…" }</span>
            </div>
            <template v-else>
            <div v-for="record in records" :key="record.data.index" class="log-row">
              <span class="line-number">{{ String(record.data.index).padStart(2, '0') }}</span>
              <time class="received-time" :datetime="record.receivedAt.toISOString()">{{ formatTime(record.receivedAt) }}</time>
              <code>{{ JSON.stringify(record.data) }}</code>
            </div>
            </template>
          </div>

          <div class="stream-footer" role="status">
            <span class="footer-indicator" :class="status" aria-hidden="true"></span>
            <span>{{ resultText }}</span>
            <span v-if="status === 'completed'" class="done-label">done</span>
          </div>
        </section>
      </div>

      <div class="endpoint-line">
        <span class="method-label">{{ requestUrl ? 'GET' : 'POST' }}</span><code>{{ endpoint }}</code>
      </div>
    </main>
    <footer class="page-footer">DeepSeek 实时 JSON <span>流式生成 · 停止后可继续接收</span></footer>
  </div>
</template>
