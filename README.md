# TransLive 智译通

基于 Web 的实时中英互译系统，采用 React + FastAPI + LibreTranslate 架构，支持输入防抖、语言切换与服务健康检测。

## 功能特性

- 实时中英互译（输入后 500ms 防抖自动翻译）
- 源语言 / 目标语言一键切换
- 翻译延迟显示与服务状态检测
- 一键复制译文、清空输入
- 开源可复现，无需付费 API

## 系统架构

```
浏览器 (React) → FastAPI 后端 → LibreTranslate (Docker)
```

## 快速开始

### 环境要求

- Docker Desktop
- Python 3.10+
- Node.js 18+

### 1. 启动翻译引擎

```bash
cd TransLive
docker compose up -d
```

首次启动会下载中英翻译模型，约需 2–5 分钟。可通过以下命令检查：

```bash
curl http://localhost:5000/languages
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

后端地址：http://localhost:8000  
API 文档：http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

### Windows 一键提示

双击 `start.bat` 可启动 Docker 服务，再按提示启动后端与前端。

## 运行实验

确保后端已启动后：

```bash
cd experiments
pip install httpx
python run_experiment.py --api http://localhost:8000
```

结果保存在 `experiments/results/experiment_results.json`。

## 项目结构

```
TransLive/
├── backend/           # FastAPI 后端
├── frontend/          # React 前端
├── experiments/       # 实验脚本与测试数据
├── docs/              # 实践报告
├── docker-compose.yml # LibreTranslate 服务
└── README.md
```

## 开源地址

GitHub: https://github.com/204404837a/TransLive

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18, Vite |
| 后端 | Python, FastAPI, httpx |
| 翻译引擎 | LibreTranslate (Argos Translate) |
| 部署 | Docker Compose |

## 许可证

MIT License
