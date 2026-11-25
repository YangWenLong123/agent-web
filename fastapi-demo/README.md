# DeepSeek 实时 JSON Demo

Vue 3 提交问题，FastAPI 调用 DeepSeek 的 `deepseek-v4-pro`，通过 SSE 实时返回 JSON 片段，完成后返回完整的 `{"answer":"..."}` 对象。

- [前端核心代码与流程](docs/frontend-guide.md)
- [后端核心代码与流程](docs/backend-guide.md)

## 配置与运行

在项目根目录安装 Python 依赖：

```bash
uv sync --locked
```

首次配置时将 `.env.example` 复制为 `.env`，填写 `DEEPSEEK_API_KEY`。已有 `.env` 时直接使用，不要覆盖。密钥仅由后端读取，`.env` 已被 Git 忽略。

```dotenv
DEEPSEEK_API_KEY=填写你的密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-v4-pro
CHAT_DB_BACKEND=mysql
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=填写你的本地数据库密码
MYSQL_DATABASE=deepseek_chat
```

先启动本地 MySQL（3306 端口）。后端启动时会自动创建 `deepseek_chat` 数据库及 `conversations`、`turns` 两张表，字符集为 `utf8mb4`，支持中文和 emoji。首次初始化的账号需有建库、建表权限，之后使用同一个库继续保存。

旧版 SQLite 历史可在**正常停止后端服务后**迁移，保持对话 ID、问答顺序和所有已保存内容：

```bash
PYTHONPATH=src .venv/bin/python -m fastapi_demo.migrate_chat
```

迁移逐条校验并在单个事务中写入，已有相同数据会跳过，存在同 ID 不同内容时回滚，源 `data/chat.sqlite3` 保留。可用 `--source 路径` 指定其他旧数据库。需要运行 SQLite 模式时显式设置 `CHAT_DB_BACKEND=sqlite` 和可选的 `CHAT_DB_PATH`；MySQL 连接失败不会自动切换到 SQLite。

安装并构建前端：

```bash
cd frontend
npm ci
npm run build
cd ..
```

启动服务（先构建，再启动）：

```bash
.venv/bin/python -m uvicorn fastapi_demo.main:app --app-dir src --reload --host 127.0.0.1 --port 8000
```

- 页面：<http://127.0.0.1:8000/>
- API 文档：<http://127.0.0.1:8000/docs>

修改前端时可在 `frontend` 目录运行 `npm run dev`，访问 <http://127.0.0.1:5173/>。Vite 将 API 和接口文档代理到 8000 端口。

## 使用方式

输入问题，点击「发送消息」。默认「内容对话」视图展示已发送的问题与实时回答正文；「实时输出 / 完整 JSON」显示生成中的 JSON 文本与最终对象；「JSON 事件」显示后端封装的每个 JSON 片段。每次发送都会追加一轮问答，已有对话不会重置。输入框的改动只影响下一条消息。

同一对话中的新问题会携带最近最多 20 轮已完成问答作为模型上下文，整个上下文按约 32000 字符限制选取；历史问答本身完整保存。后端使用 JSON Output 模式、`thinking: {"type":"disabled"}` 和最多 2048 个输出 token。模型未返回完整合法对象时会显示错误，保留已收到的片段。

停止仅暂停前端接收，已创建的后台任务仍然调用模型并缓存结果，仍可能产生模型用量。点击「继续接收」使用同一个任务和事件游标补收，**不会再次调用模型**。本轮接收完成后，点击「发送消息」会在当前对话中追加新任务。「新建对话」开始独立上下文，已有历史仍可切回；它不会取消已经创建的后台任务。若在创建任务响应到达前停止，前端尚无任务 ID，无法继续，后端可能已经开始生成。

问答持久化到本地 MySQL 的 `deepseek_chat` 数据库，刷新页面和服务重启后仍可读取。页面默认恢复上次使用的对话，可通过「历史对话」切换；生成中重启服务时，会保留已落盘的部分内容并标记中断。连接密码仅放在已被 Git 忽略的后端 `.env` 中。

SSE 事件任务缓存最多保留 16 条，满时淘汰最早创建的已完成任务；全部运行中时拒绝新任务。任务结束后保留约 30 分钟，访问或新建任务时清理过期记录。服务重启后事件缓存丢失，但已保存的问答保留。当前为本机、单进程示例，运行一个 Uvicorn worker；多进程部署需共享任务存储，向多人开放前需增加身份认证与配额控制。

## 接口协议

### 1. 提交问题

```bash
curl -sS -X POST 'http://127.0.0.1:8000/api/sse/generations' \
  -H 'Content-Type: application/json' \
  -d '{"content":"请介绍 SSE"}'
```

HTTP 201 响应：

```json
{"stream_id":"返回的32位任务ID","model":"deepseek-v4-pro","conversation_id":"对话ID","turn_id":"本轮问答ID","title":"对话标题","context_count":0}
```

后续追问时，在请求体中同时传入 `conversation_id`；不传则创建新对话。`context_count` 表示本轮实际参考的历史问答轮数。

`GET /api/sse/conversations` 读取历史对话列表；`GET /api/sse/conversations/{conversation_id}` 读取该对话的全部问答及结果。

### 2. 订阅或继续接收

用上一步真实返回的 `stream_id` 替换占位符：

```bash
curl -N 'http://127.0.0.1:8000/api/sse/jsonlines?stream_id=返回的32位任务ID&after_id=0'
```

响应为 `text/event-stream`，每个 `data:` 字段是一行独立 JSON。普通数据：

```text
id: 1
data: {"type":"delta","index":1,"content":"{\"answer\":"}

```

`content` 是 JSON 文本片段，单个片段不一定能独立解析；前端拼接它们获得正在生成的 JSON。后端在完成时解析、校验完整对象，然后发送：

```text
id: 3
event: done
data: {"type":"done","count":2,"result":{"answer":"SSE 是服务端推送技术。"},"model":"deepseek-v4-pro","usage":null}

```

错误使用 `event: failure`，携带 `{"type":"error","message":"错误说明"}`，不转发上游原始错误或密钥。

`after_id` 表示最后成功处理的 SSE 事件 ID，默认 0；继续接收时设置为上次记录的 ID。等待模型期间每 15 秒发送一次 SSE 注释心跳。

## 验证

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
cd frontend
npm test
npm run build
```

自动测试使用模拟上游，不消耗真实 API 额度。真实联调时，通过页面提交问题，验证多轮追加、记忆追问、刷新恢复、历史切换、完整 JSON、停止后继续和事件序号连续性。

本地 MySQL 集成测试：

```bash
RUN_MYSQL_TESTS=1 PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
```

测试会创建并清理随机命名的 `deepseek_test_*` 独立库，不改动 `deepseek_chat`。覆盖 MySQL 持久化、中文及 emoji、并发防重、上下文记忆、迁移校验与回滚，以及真实数据库下的历史 API。未设置 `RUN_MYSQL_TESTS=1` 时会跳过这些集成测试。
