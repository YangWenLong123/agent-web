# 什么是uv?

`uv` 是 Astral 开发的 Python 项目与依赖管理工具。它可以统一完成 Python 版本安装、虚拟环境、依赖安装、版本锁定和项目命令运行，定位类似前端中的 `pnpm`。

`uv` 可以替代 pip、virtualenv、pip-tools、pyenv 等工具，提供依赖管理、虚拟环境创建、Python 版本管理等一站式服务。

# uv 的优势

- 速度极快：由于使用 Rust 编写，uv 的性能远超 pip 和其他包管理工具，安装依赖的速度可以提升 10-100 倍。
- 功能集成：集依赖解析、包安装、环境管理和 Python 版本管理于一体，无需再安装和学习多个工具。
- 确定性构建：uv 会生成 uv.lock 文件，确保在任何环境中都能安装完全相同的依赖版本，避免"在我机器上能运行"的问题。
- 与现有工具兼容：uv 可以处理 requirements.txt 和 pyproject.toml，可以无缝替代现有工作流中的 pip。

# 安装 uv

macOS：

```sh
brew install uv
```

macOS/Linux 官方脚本：

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell：

```sh
irm https://astral.sh/uv/install.ps1 | iex
```

验证：

```sh
uv --version
```

# 常用命令集合

```sh
# Python 版本
uv python list                 # 查看可用/已安装版本
uv python install 3.12         # 安装 Python 3.12
uv python pin 3.12             # 当前项目固定使用 3.12
uv python find                 # 查看项目实际使用的 Python

# 创建项目
uv init my-project             # 创建新项目目录
uv init                        # 在当前目录初始化
uv init --app my-api           # 创建应用项目
uv init --lib my-package       # 创建可发布的库项目

# 虚拟环境
uv venv                        # 创建 .venv
uv venv --python 3.12          # 使用指定版本创建
rm -rf .venv && uv sync        # 重建环境，谨慎确认当前目录

# 依赖管理
uv add fastapi                 # 添加运行依赖
uv add "pydantic>=2.0"         # 添加带版本约束的依赖
uv add --dev pytest ruff mypy  # 添加开发依赖
uv remove fastapi              # 删除依赖
uv lock                        # 解析依赖并更新 uv.lock
uv lock --check                # 检查锁文件是否需要更新
uv sync                        # 按 pyproject.toml/uv.lock 同步环境
uv sync --frozen               # 严格使用现有 lock，不允许修改
uv sync --no-dev               # 不安装开发依赖
uv tree                        # 显示依赖树

# 运行命令
uv run python main.py          # 运行 Python 文件
uv run python -m app           # 运行 Python 模块
uv run pytest                  # 运行测试
uv run ruff check .            # 运行代码检查
uv run mypy app                # 运行类型检查
uv run uvicorn app.main:app --reload

# pip 兼容模式
uv pip install requests        # 类似 pip install
uv pip install -r requirements.txt
uv pip list
uv pip freeze

# 临时运行工具
uvx ruff check .               # 临时安装并运行 Ruff
uvx black .                    # 临时运行 Black

# 导出传统依赖文件
uv export --format requirements-txt > requirements.txt
```

# 下载已有 uv 项目后运行

```sh
git clone <repository-url>
cd <project-directory>

uv python install
uv sync --frozen
uv run python main.py
```

FastAPI 项目一般运行：

```sh
uv run uvicorn app.main:app --reload
```

`uv run` 会自动使用项目的 `.venv`，通常不需要手动执行 `source .venv/bin/activate`。

如果需要进入虚拟环境：

```sh
source .venv/bin/activate      # macOS/Linux
```

```sh
.venv\Scripts\Activate.ps1     # Windows PowerShell
```

# 运行传统 requirements 项目

项目只有 `requirements.txt` 时：

```sh
cd existing-project

uv venv --python 3.12
uv pip install -r requirements.txt
uv run python main.py
```

也可以迁移成 uv 项目：

```sh
uv init
uv add -r requirements.txt
uv lock
uv sync
```

迁移完成后，应提交 `pyproject.toml` 和 `uv.lock`，并将 `.venv`/ 写入 `.gitignore`。

# 日常开发流程

```sh
git pull
uv sync
uv add <新依赖>
uv run pytest
uv run python main.py
```

团队或 CI 中推荐：

```sh
uv sync --frozen
uv run ruff check .
uv run pytest
```

最需要记住的五个命令是：`uv init`、`uv add`、`uv sync`、`uv run` 和 `uv lock`。

# 和前端指令对比

| Python/uv             | JavaScript                                  |
| --------------------- | ------------------------------------------- |
| `uv init`             | `npm init` / `pnpm init`                    |
| `uv add axios`        | `npm install axios` / `pnpm add axios`      |
| `uv remove axios`     | `npm uninstall axios` / `pnpm remove axios` |
| `uv sync`             | `npm install` / `pnpm install`              |
| `uv sync --frozen`    | `npm ci` / `pnpm install --frozen-lockfile` |
| `uv run pytest`       | `pnpm exec vitest` / `npx vitest`           |
| `uv add --dev pytest` | `pnpm add -D vitest`                        |
| `uv sync --no-dev`    | `pnpm install --prod`                       |
