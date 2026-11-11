# UnudeAI Clone — 多模型 AI 创作平台

参考 [unudeai.com](https://unudeai.com) 实现的前后端分离多模型 AI 创作平台 MVP：文生图、文生视频、AI 对话、社区作品流。

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python 3.13 + FastAPI + SQLAlchemy + SQLite + JWT |
| 前端 | Vue 3 + Vite + Vue Router（移动端优先，深紫暗色主题） |
| 多模型 | Provider 抽象层：Pollinations(免费) / SiliconFlow / Mock，失败自动降级 |

## 快速启动

```bash
# 后端 (端口 8000)
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000 --host 127.0.0.1

# 前端 (端口 5173, 已配置 /api /media 代理)
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173 ，注册新用户自动赠送 100 积分。

## 多模型接入（backend/.env）

- **测试期**：`DEFAULT_PROVIDER=pollinations`，免注册免 Key，开箱即用
- **升级 SiliconFlow**（推荐，注册 https://siliconflow.cn 送额度）：
  1. 在 `.env` 填入 `SILICONFLOW_API_KEY=sk-xxxx`
  2. 重启后端，Flux 生图 / Wan2.2 文生视频 / Qwen 对话自动启用（未配置时自动降级到免费通道）
- 新模型只需在 `app/providers/` 增加一个 Provider 类并在 `registry.py` 的 `MODEL_CATALOG` 注册一行

## 功能模块（对齐参考站）

| Tab | 功能 | 状态 |
|-----|------|------|
| Home | 作品推荐瀑布流 + 点赞 | ✅ |
| Discover | 社区公开作品广场 | ✅ |
| Short | AI 视频作品流（悬停播放） | ✅ |
| Create | 文生图/文生视频工作台：模型选择、比例、进度条、结果预览 | ✅ |
| AI Lover | AI 助手聊天（多轮上下文） | ✅ |
| My | 个人资料、积分余额、我的作品 | ✅ |

## 核心机制

- **异步生成任务**：提交后进线程池执行，前端 1.5s 轮询任务进度，产物落盘 `backend/media/`
- **积分计费**：按模型定价扣积分，生成失败自动退还
- **静默降级**：SiliconFlow 未配 Key → 生图走 Pollinations、视频走 Mock、对话走 Pollinations

## 目录结构

```
backend/app
  api/          # auth / create / works / chat 路由
  providers/    # base 抽象 + pollinations / siliconflow / mock + registry 模型目录
  services/     # 生成任务执行器
  core/         # 配置 / 安全 / 数据库
frontend/src
  views/        # Home Discover Short Create AILover My Login
  components/   # TabBar / WorksFeed
```
