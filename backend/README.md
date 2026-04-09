# 家政管理系统后端

基于 FastAPI + MySQL + Redis 的家政管理系统后端服务

## 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0
- **缓存**: Redis
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt

## 功能特性

- ✅ 用户注册登录（邮箱验证码）
- ✅ JWT Token 认证
- ✅ 三种角色：普通用户、家政阿姨、管理员
- ✅ 用户信息管理
- ✅ 密码修改
- 🚧 家政阿姨申请审核（待开发）
- 🚧 预约管理（待开发）
- 🚧 订单管理（待开发）

## 数据库设计

### 核心表结构

1. **users** - 用户表
   - 支持三种角色：user（普通用户）、worker（家政阿姨）、admin（管理员）
   - 所有用户注册时默认为普通用户
   - 申请成为家政阿姨需要提交资料审核

2. **worker_applications** - 家政阿姨申请表
3. **worker_profiles** - 家政阿姨详细信息表
4. **services** - 服务项目表
5. **appointments** - 预约订单表
6. **announcements** - 公告表
7. **time_slots** - 时间段配置表
8. **favorites** - 收藏表
9. **browse_history** - 浏览历史表

详见 `database_design.sql`

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

已配置好 `.env` 文件，数据库信息：
- 数据库: housekeeping@1.15.22.194
- Redis: 1.15.22.194 (DB 5)

### 3. 初始化数据库

```bash
# 连接到MySQL并执行
mysql -h 1.15.22.194 -u housekeeping -p housekeeping < database_design.sql
```

### 4. 启动服务

```bash
python run.py
```

服务将在 http://localhost:8000 启动

### 5. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口

### 认证相关 (/api/v1/auth)

#### 1. 发送验证码
```http
POST /api/v1/auth/send-code
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**响应**（开发模式会返回验证码）:
```json
{
  "code": 200,
  "message": "验证码已生成（开发模式）",
  "data": {
    "email": "user@example.com",
    "verification_code": "123456",
    "expire_seconds": 300
  }
}
```

#### 2. 用户注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "code": "123456",
  "nickname": "张三"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "nickname": "张三",
      "role": "user",
      "status": "active",
      "created_at": "2024-12-09T12:00:00"
    }
  }
}
```

#### 3. 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "account": "user@example.com",
  "password": "password123"
}
```

#### 4. 获取当前用户信息
```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

#### 5. 更新用户信息
```http
PUT /api/v1/auth/update-profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "nickname": "新昵称",
  "phone": "13800138000",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

#### 6. 修改密码
```http
POST /api/v1/auth/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "old_password": "oldpass123",
  "new_password": "newpass123"
}
```

## 开发说明

### 项目结构

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── auth.py          # 认证API
│   ├── core/
│   │   ├── config.py            # 配置
│   │   ├── database.py          # 数据库连接
│   │   ├── redis_client.py      # Redis客户端
│   │   └── security.py          # 安全相关（JWT、密码）
│   ├── models/
│   │   └── user.py              # 用户模型
│   ├── schemas/
│   │   └── user.py              # 用户数据模式
│   ├── utils/
│   │   └── helpers.py           # 辅助函数
│   └── main.py                  # 应用入口
├── .env                         # 环境变量
├── requirements.txt             # 依赖
├── run.py                       # 启动脚本
└── database_design.sql          # 数据库设计
```

### 角色说明

1. **user（普通用户）**
   - 默认注册角色
   - 可以浏览家政阿姨、预约服务
   - 可以申请成为家政阿姨

2. **worker（家政阿姨）**
   - 由普通用户申请并审核通过后获得
   - 可以接单、管理订单
   - 拥有详细的个人档案

3. **admin（管理员）**
   - 管理所有用户
   - 审核家政阿姨申请
   - 管理服务项目、公告等

## 下一步开发

- [ ] 家政阿姨申请功能
- [ ] 家政阿姨列表和详情
- [ ] 预约功能
- [ ] 订单管理
- [ ] 评价系统
- [ ] 收藏和浏览历史
- [ ] 公告管理
- [ ] 管理后台功能

## 注意事项

1. 当前为开发模式，验证码会直接返回，生产环境需要集成邮件服务
2. 确保 MySQL 和 Redis 服务正常运行
3. JWT Token 有效期为 7 天（10080分钟）
4. 所有密码使用 bcrypt 加密存储
