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

## Docker 生产部署

项目根目录已提供生产部署文件：

```text
Dockerfile
docker-compose.yml
.dockerignore
```

启动前先准备后端环境变量：

```bash
copy backend\.env.example backend\.env
```

启动 FastAPI、MySQL、Redis：

```bash
docker compose up -d --build
```

应用容器会等待 MySQL ready，自动执行 `alembic upgrade head`，再启动 FastAPI。

Docker MySQL 首次启动会自动执行 `backend/scripts/init_mysql.sql`，创建 `pet_planet` 数据库、`pet` 用户并授权；本地 MySQL 可手动执行 `mysql -u root -p < backend/scripts/init_mysql.sql`。

## 团队协作

先阅读：

- `docs/项目开发协作规范.md`
- `docs/给队友的使用说明.md`
- `backend/README.md`

四名后端成员统一基于 `backend` 开发，不要各自新建后端工程。
