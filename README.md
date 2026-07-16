# 合同管理系统

一个基于 Docker 的企业合同管理系统，支持合同生命周期管理、到期提醒和多渠道通知。

## 功能特性

- **合同管理**: 登记、查询、详情、附件上传与预览
- **到期预警**: 自动计算合同状态，支持提前提醒天数配置
- **数据看板**: 统计概览、环比数据、月度趋势图表
- **多渠道通知**: 邮件、企业微信、Server酱（推送到个人微信）
- **自动提醒**: 后台定时检查快到期合同，自动发送通知
- **用户管理**: 角色权限控制（管理员/经理/查看者）

## 技术栈

- **前端**: Vue 3 + Vite + Element Plus + Vue Router + Pinia
- **后端**: FastAPI + SQLAlchemy + SQLite + Pydantic
- **认证**: JWT Token
- **部署**: Docker 单容器架构

## 快速部署

### 方式一: Docker Hub 拉取

```bash
# 拉取镜像
docker pull your-username/contract-management:latest

# 创建数据目录
mkdir -p data

# 启动容器
docker run -d \
  --name contract-management \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  your-username/contract-management:latest

# 访问系统
# http://localhost:8000
```

### 方式二: 本地构建

```bash
# 克隆仓库
git clone https://github.com/your-username/contract-management.git
cd contract-management

# 复制环境变量配置
cp .env.example .env
# 编辑 .env 修改 JWT 密钥等配置（可选）

# 构建并启动
docker-compose up -d --build

# 访问系统
# http://localhost:8000
```

## 默认账号

首次启动后使用以下账号登录:

- 用户名: `admin`
- 密码: `admin123`

> 建议在生产环境中修改默认密码

## 环境变量

在 `.env` 文件中可配置:

| 变量 | 默认值 | 说明 |
|------|--------|------|
| JWT_SECRET_KEY | change_me_in_production | JWT 签名密钥 |
| JWT_EXPIRE_HOURS | 8 | Token 有效期（小时） |

## 目录结构

```
contract-management/
├── app/
│   ├── main.py          # 后端主程序
│   ├── requirements.txt # Python 依赖
│   └── static/          # 前端构建产物
├── frontend/
│   ├── src/             # Vue 3 源码
│   ├── package.json
│   └── vite.config.js
├── data/                # 持久化数据（Docker 卷）
│   ├── contracts.db     # SQLite 数据库
│   └── uploads/         # 上传文件
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .github/
    └── workflows/
        └── docker-build.yml  # 自动构建配置
```

## 自动提醒配置

系统支持三种通知渠道:

1. **邮件 SMTP**: 在「系统管理 → 通知配置」中填写 SMTP 服务器信息
2. **企业微信**: 配置群机器人 Webhook 地址
3. **Server酱**: 访问 sct.ftqq.com 获取 SendKey，推送到个人微信

开启「自动提醒」开关后，系统每天自动检查快到期合同并发送通知。

## GitHub Actions 自动构建

推送到 main/master 分支时自动构建 Docker 镜像并推送到 Docker Hub。

需要在 GitHub 仓库设置中配置 Secrets:

- `DOCKERHUB_USERNAME`: Docker Hub 用户名
- `DOCKERHUB_TOKEN`: Docker Hub Access Token

## 许可证

MIT License