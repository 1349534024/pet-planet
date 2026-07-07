n# 宠物星球后端统一框架

这是四人后端协作用的统一 FastAPI 框架。A 负责维护公共底座，B/C/D 在此基础上按模块扩展。

## 1. 当前已包含

- FastAPI 启动入口。
- SQLAlchemy 2.x 数据库连接。
- Alembic 迁移配置。
- 统一响应结构。
- 统一错误码和异常处理。
- JWT token 生成和鉴权依赖。
- 分页参数工具。
- RabbitMQ 事件发布封装。
- DeepSeek/LangChain 接入占位。
- A 模块示例：认证、用户、地址、宠物档案、成长记录、提醒、文件上传凭证。

## 2. 安装依赖

建议先创建虚拟环境：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 3. 环境变量

复制环境变量模板：

```bash
copy .env.example .env
```

根据本地数据库修改：

```text
DATABASE_URL=mysql+pymysql://pet:pet123456@127.0.0.1:3306/pet_planet
```

或：

```text
DATABASE_URL=postgresql+psycopg://pet:pet123456@127.0.0.1:5432/pet_planet
```

## 4. 启动服务

```bash
uvicorn app.main:app --reload
```

启动后访问：

```text
http://127.0.0.1:8000/docs
```

## 5. 数据库迁移

首次生成迁移：

```bash
alembic revision --autogenerate -m "add base user pet tables"
```

执行迁移：

```bash
alembic upgrade head
```

以后任何人改表，都必须新增 Alembic 迁移，禁止直接手改数据库。

## 6. 开发环境登录说明

短信登录接口：

```text
POST /api/v1/auth/login/sms
```

开发环境默认验证码：

```text
123456
```

请求示例：

```json
{
  "phone": "13800000000",
  "code": "123456"
}
```

返回 `access_token` 后，后续接口请求头加：

```http
Authorization: Bearer <access_token>
```

## 7. 每个人怎么写自己的模块

新增模块统一按这 5 个文件写：

```text
app/api/v1/模块名.py
app/models/模块名.py
app/schemas/模块名.py
app/services/模块名_service.py
app/repositories/模块名_repo.py
```

例如 B 做订单：

```text
app/api/v1/orders.py
app/models/order.py
app/schemas/order.py
app/services/order_service.py
app/repositories/order_repo.py
```

然后在：

```text
app/api/v1/router.py
```

注册路由。

## 8. 四人模块边界

### A

- `auth`
- `users`
- `pets`
- `reminders`
- `files`
- `roles`
- 公共 core/db/tasks/ai 框架

### B

- `products`
- `cart`
- `orders`
- `payments`
- `after_sales`
- `pet_coins`
- `coupons`

### C

- `merchants`
- `adoptions`
- `live_pets`
- `service_bookings`

### D

- `admin`
- `audit`
- `risk`
- `messages`
- `statistics`
- `operation_configs`

## 9. 统一响应格式

成功：

```json
{
  "code": "SUCCESS",
  "message": "success",
  "data": {}
}
```

失败：

```json
{
  "code": "VALIDATION_ERROR",
  "message": "错误信息",
  "data": null
}
```

## 10. 提交前检查

提交代码前确认：

- 服务能启动。
- 新增接口在 `/docs` 能看到。
- 修改表结构后已生成 Alembic 迁移。
- 没有提交 `.env`。
- 没有在日志里打印手机号、身份证、token 等敏感明文。

