# 宠物星球 / Pet Planet

宠物星球是一个综合养宠 App 项目，当前仓库先提供四人后端协作使用的统一开发框架。

## 目录

```text
backend/  FastAPI 后端统一框架
docs/     项目开发规范、队友使用说明
```

## 后端启动

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

启动后访问：

```text
http://127.0.0.1:8000/docs
```

## 团队协作

先阅读：

- `docs/项目开发协作规范.md`
- `docs/给队友的使用说明.md`
- `backend/README.md`

四名后端成员统一基于 `backend` 开发，不要各自新建后端工程。
