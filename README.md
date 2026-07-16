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

### 方式一: Portainer Stacks（推荐）

1. 打开 Portainer → Stacks → Add Stack
2. 填写名称: `contract-management`
3. 在 Web editor 中粘贴以下内容：

```yaml
name: contract-management

services:
  contract-management:
    image: ghcr.io/your-username/contract-management:latest
    container_name: contract-management
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - contract_data:/data
    environment:
      - ADMIN_PASSWORD=your-admin-password

volumes:
  contract_data:
    driver: local
```

4. 点击 "Deploy the stack"

### 方式二: Docker 命令

```bash
docker run -d \
  --name contract-management \
  -p 8000:8000 \
  -v contract_data:/data \
  -e ADMIN_PASSWORD=your-admin-password \
  ghcr.io/your-username/contract-management:latest
```

### 方式三: 本地开发构建

```bash
git clone https://github.com/your-username/contract-management.git
cd contract-management
docker-compose up -d --build
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| APP_PORT | 8000 | 映射端口 |
| ADMIN_USERNAME | admin | 管理员用户名 |
| ADMIN_PASSWORD | admin123 | 管理员密码（必须修改） |
| ADMIN_EMAIL | admin@contract.com | 管理员邮箱 |

> **注意**: JWT_SECRET_KEY 会在首次启动时自动生成并保存到数据库，无需手动配置。

## 默认账号

首次启动后使用以下账号登录:

- 用户名: `admin`（可通过环境变量修改）
- 密码: `admin123`（**生产环境务必修改**）

## 目录结构

```
contract-management/
├── app/
│   ├── main.py          # 后端主程序
│   └── requirements.txt # Python 依赖
├── frontend/
│   ├── src/             # Vue 3 源码
│   ├── package.json
│   └── vite.config.js
├── .github/
│   └── workflows/
│       └── docker-build.yml  # GitHub Actions 自动构建
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## GitHub Actions 自动构建

推送到 main/master 分支时自动构建并推送到 **GitHub Container Registry (ghcr.io)**。

### 首次使用前的配置

在 GitHub 仓库中开启 Packages 权限：
1. 打开仓库 → Settings → Actions → General
2. 在 **Workflow permissions** 部分，选择 **Read and write permissions**
3. 点击 **Save**

### 镜像地址

镜像会被推送到：
```
ghcr.io/你的用户名/你的仓库名:latest
```

例如你的仓库是 `https://github.com/myusername/contract-management`，则镜像地址是：
```
ghcr.io/myusername/contract-management:latest
```

### 更新部署

每次 push 代码后：
1. GitHub Actions 自动构建并推送新镜像到 ghcr.io
2. 在 Portainer 中点击 "Update stack" → "Re-pull image and redeploy"

## 许可证

MIT License