"""
合同管理系统 - 单容器版本
使用 SQLite 数据库 + 本地文件存储
"""
import os
import uuid
import logging
import smtplib
import json
import threading
import urllib.request
import urllib.error
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date, timedelta, timezone
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Numeric, Date, Text, Enum, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import JWTError, jwt
import aiosqlite
import asyncio

# ========== 配置 ==========
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/contracts.db")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "8"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@contract.com")

# 确保目录存在
os.makedirs(os.path.dirname(DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ========== 数据库模型 ==========
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    viewer = "viewer"

class ContractType(str, enum.Enum):
    repair = "维修合同"
    maintenance = "维保合同"
    external_repair = "外修合同"
    decoration = "装修合同"

class ContractStatus(str, enum.Enum):
    active = "执行中"
    expiring = "即将到期"
    expired = "已到期"
    terminated = "已终止"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(20), default="viewer", nullable=False)
    is_active = Column(Boolean, default=True)
    wechat_openid = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    contract_no = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    party_a = Column(String(100), nullable=False)
    party_b = Column(String(100), nullable=False)
    amount = Column(Numeric(15, 2), nullable=True)
    contract_type = Column(String(20), nullable=False)
    sign_date = Column(Date, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), default="执行中")
    remind_days = Column(Integer, default=30)
    file_path = Column(String(500), nullable=True)
    remark = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    recipient = Column(String(100), nullable=True)
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Setting(Base):
    __tablename__ = "settings"
    key = Column(String(50), primary_key=True)
    value = Column(Text, nullable=True)

# 创建表
logging.info("[init] 创建数据库表...")
Base.metadata.create_all(bind=engine)

# ========== JWT 密钥自动生成 ==========
def init_jwt_secret():
    from sqlalchemy import text
    env_key = os.getenv("JWT_SECRET_KEY")
    if env_key and env_key != "change_me_in_production":
        logging.info("[init] 使用环境变量中的 JWT 密钥")
        return env_key
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT value FROM settings WHERE key = 'jwt_secret_key'"))
            row = result.first()
            if row:
                logging.info("[init] 从数据库读取 JWT 密钥")
                return row[0]
            import secrets
            new_key = secrets.token_hex(32)
            conn.execute(text("INSERT OR IGNORE INTO settings (key, value) VALUES ('jwt_secret_key', :key)"), {"key": new_key})
            conn.commit()
            logging.info("[init] 自动生成 JWT 密钥")
            return new_key
    except Exception as e:
        logging.error(f"[init] JWT 密钥初始化失败: {e}")
        import secrets
        new_key = secrets.token_hex(32)
        logging.info("[init] 使用内存生成的临时 JWT 密钥")
        return new_key

JWT_SECRET_KEY = init_jwt_secret()

# ========== 自动迁移（为已存在的表补充新增列）==========
def run_migrations():
    """检查每个表的实际列，对缺失的列执行 ALTER TABLE ADD COLUMN。
    SQLite 仅支持 ADD COLUMN，不能修改或删除列，所以这里只处理新增字段。"""
    from sqlalchemy import inspect, text
    insp = inspect(engine)
    with engine.connect() as conn:
        for table_name, table_obj in Base.metadata.tables.items():
            if not insp.has_table(table_name):
                continue
            existing_cols = {col["name"] for col in insp.get_columns(table_name)}
            for col_name, col_obj in table_obj.columns.items():
                if col_name in existing_cols:
                    continue
                # 构造列类型 SQL
                col_type = col_obj.type.compile(engine.dialect)
                nullable = "" if col_obj.nullable else " NOT NULL"
                default = ""
                if col_obj.default is not None and col_obj.default.arg is not None:
                    try:
                        default_val = col_obj.default.arg() if callable(col_obj.default.arg) else col_obj.default.arg
                        if isinstance(default_val, (int, float)):
                            default = f" DEFAULT {default_val}"
                        elif isinstance(default_val, bool):
                            default = f" DEFAULT {int(default_val)}"
                        elif isinstance(default_val, str):
                            default = f" DEFAULT '{default_val}'"
                    except Exception:
                        pass
                sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}{nullable}{default}"
                try:
                    conn.execute(text(sql))
                    logging.info(f"[migration] 已为 {table_name} 添加列 {col_name}")
                except Exception as e:
                    logging.warning(f"[migration] 添加 {table_name}.{col_name} 失败: {e}")
        conn.commit()

run_migrations()

# ========== 工具函数 ==========
# 密码哈希工具
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

class PwdContext:
    def hash(self, password: str) -> str:
        return hash_password(password)
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)

pwd_context = PwdContext()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 内存缓存替代 Redis
_token_blacklist = set()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_token(user_id: int, username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode({"sub": str(user_id), "username": username, "exp": expire},
                      JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if token in _token_blacklist:
        raise HTTPException(status_code=401, detail="Token已失效")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user = db.query(User).filter(User.id == int(payload["sub"])).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="用户不存在或已禁用")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token无效")

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user

def calc_status(c: Contract) -> str:
    today = date.today()
    if c.end_date < today:
        return "已到期"
    if (c.end_date - today).days <= c.remind_days:
        return "即将到期"
    return "执行中"

def contract_dict(c: Contract) -> dict:
    today = date.today()
    days_left = (c.end_date - today).days
    return {
        "id": c.id, "contract_no": c.contract_no, "title": c.title,
        "party_a": c.party_a, "party_b": c.party_b,
        "amount": float(c.amount) if c.amount else None,
        "contract_type": c.contract_type, "sign_date": str(c.sign_date) if c.sign_date else None,
        "start_date": str(c.start_date), "end_date": str(c.end_date),
        "status": c.status, "remind_days": c.remind_days,
        "file_path": c.file_path, "remark": c.remark,
        "days_left": days_left, "created_at": str(c.created_at)[:10]
    }

def get_smtp_config(db: Session = None) -> dict:
    """从数据库读取 SMTP 配置，回退到环境变量"""
    if db is None:
        db = SessionLocal()
        try:
            rows = db.query(Setting).all()
        finally:
            db.close()
    else:
        rows = db.query(Setting).all()
    config = {r.key: r.value for r in rows}
    return {
        "host": config.get("smtp_host") or SMTP_HOST,
        "port": int(config.get("smtp_port") or SMTP_PORT),
        "user": config.get("smtp_user") or SMTP_USER,
        "password": config.get("smtp_password") or SMTP_PASSWORD,
    }

def get_wechat_webhook_url(db: Session = None) -> str:
    """获取企业微信 Webhook URL"""
    if db is None:
        db = SessionLocal()
        try:
            row = db.query(Setting).filter(Setting.key == "wechat_webhook_url").first()
            return row.value if row else ""
        finally:
            db.close()
    else:
        row = db.query(Setting).filter(Setting.key == "wechat_webhook_url").first()
        return row.value if row else ""

def send_wechat_message(webhook_url: str, content: str):
    """发送企业微信 Webhook 消息"""
    if not webhook_url:
        raise HTTPException(status_code=500, detail="企业微信 Webhook 未配置")
    
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("errcode", 0) != 0:
                raise Exception(result.get("errmsg", "发送失败"))
            return True
    except urllib.error.URLError as e:
        logging.error(f"企业微信发送失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"企业微信发送失败: {str(e)}")
    except Exception as e:
        logging.error(f"企业微信发送失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"企业微信发送失败: {str(e)}")

def get_setting(db: Session, key: str, default: str = "") -> str:
    """读取单个配置项"""
    row = db.query(Setting).filter(Setting.key == key).first()
    return row.value if row else default

def set_setting(db: Session, key: str, value: str):
    """写入单个配置项"""
    existing = db.query(Setting).filter(Setting.key == key).first()
    if existing:
        existing.value = value
    else:
        db.add(Setting(key=key, value=value))

def get_serverchan_keys(db: Session = None) -> list[str]:
    """获取所有 Server酱 SendKey 列表"""
    if db is None:
        db = SessionLocal()
        try:
            val = get_setting(db, "serverchan_keys")
        finally:
            db.close()
    else:
        val = get_setting(db, "serverchan_keys")
    if not val:
        return []
    return [k.strip() for k in val.split("\n") if k.strip()]

def send_serverchan(sendkey: str, title: str, content: str):
    """通过 Server酱 发送微信通知"""
    if not sendkey:
        raise Exception("Server酱 SendKey 未配置")
    
    data = urllib.parse.urlencode({
        "title": title,
        "desp": content
    }).encode('utf-8')
    
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    try:
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("code", 0) != 0:
                raise Exception(result.get("message", "发送失败"))
            return True
    except Exception as e:
        logging.error(f"Server酱发送失败: {str(e)}")
        raise Exception(f"Server酱发送失败: {str(e)}")

def send_email(to_email: str, subject: str, body: str, db: Session = None):
    cfg = get_smtp_config(db)
    if not cfg["host"]:
        raise HTTPException(status_code=500, detail="邮件服务未配置，请先在系统管理-邮件配置中设置SMTP信息")
    
    msg = MIMEMultipart()
    msg['From'] = cfg["user"]
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL(cfg["host"], cfg["port"])
        server.login(cfg["user"], cfg["password"])
        server.sendmail(cfg["user"], to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        logging.error(f"邮件发送失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"邮件发送失败: {str(e)}")

# ========== Pydantic 模型 ==========
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "viewer"

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class ContractCreate(BaseModel):
    contract_no: str
    title: str
    party_a: str
    party_b: str
    amount: Optional[float] = None
    contract_type: str
    sign_date: Optional[str] = None
    start_date: str
    end_date: str
    remind_days: int = 30
    remark: Optional[str] = None
    file_path: Optional[str] = None

class NotificationSend(BaseModel):
    contract_ids: list[int] = []
    to_emails: list[str] = []
    message: Optional[str] = None
    send_wechat: bool = False
    send_serverchan: bool = False

class SmtpConfig(BaseModel):
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""

class WechatConfig(BaseModel):
    wechat_webhook_url: str = ""

class TestEmail(BaseModel):
    to_email: str

class TestWechat(BaseModel):
    pass

class ServerChanConfig(BaseModel):
    serverchan_keys: str = ""

class AutoRemindConfig(BaseModel):
    auto_remind_enabled: bool = False
    auto_remind_days: int = 30

# ========== 创建 FastAPI 应用 ==========
app = FastAPI(title="合同管理系统", version="2.0.0")

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"])

# ========== 初始化管理员 ==========
def seed_admin():
    db = SessionLocal()
    try:
        if not db.query(User).first():
            admin = User(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                hashed_password=pwd_context.hash(ADMIN_PASSWORD),
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            logging.info(f"[seed] 默认管理员账号已创建: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    finally:
        db.close()

@app.on_event("startup")
def startup():
    seed_admin()
    # 启动自动提醒后台线程
    remind_thread = threading.Thread(target=auto_remind_loop, daemon=True)
    remind_thread.start()
    logging.info("[startup] 自动提醒后台线程已启动")

# ========== 自动提醒 ==========
_last_remind_date = None  # 记录上次提醒日期，每天只执行一次

def auto_remind_loop():
    """后台线程：每小时检查一次，每天执行一次自动提醒"""
    global _last_remind_date
    while True:
        try:
            today = date.today()
            if _last_remind_date != today:
                db = SessionLocal()
                try:
                    enabled = get_setting(db, "auto_remind_enabled") == "true"
                    if enabled:
                        do_auto_remind(db)
                        _last_remind_date = today
                        logging.info(f"[auto-remind] {today} 自动提醒已执行")
                finally:
                    db.close()
        except Exception as e:
            logging.error(f"[auto-remind] 自动提醒异常: {str(e)}")
        # 每小时检查一次
        threading.Event().wait(3600)

def do_auto_remind(db: Session):
    """执行自动提醒：查找快到期合同，通过已配置的渠道发送"""
    remind_days = int(get_setting(db, "auto_remind_days", "30"))
    today = date.today()
    deadline = today + timedelta(days=remind_days)
    
    # 查找在提醒范围内的合同（未终止的）
    contracts = db.query(Contract).filter(
        Contract.end_date <= deadline,
        Contract.end_date >= today,
        Contract.status != "已终止"
    ).order_by(Contract.end_date).all()
    
    if not contracts:
        return {"message": "无需提醒的合同"}
    
    # 构建通知内容
    contract_lines = []
    for c in contracts:
        days_left = (c.end_date - today).days
        contract_lines.append(f"- {c.title}（{c.contract_no}）\n  到期：{c.end_date} | 剩 {days_left} 天")
    
    title = f"【合同到期提醒】{len(contracts)}个合同即将到期"
    content = f"以下合同将在 {remind_days} 天内到期，请及时处理：\n\n" + "\n".join(contract_lines)
    
    results = {"email": 0, "wechat": False, "serverchan": 0, "errors": []}
    
    # 1. 邮件通知（发送给所有用户邮箱）
    try:
        cfg = get_smtp_config(db)
        if cfg["host"]:
            users = db.query(User).filter(User.is_active == True, User.email != "").all()
            email_list = [u.email for u in users if u.email]
            for email in email_list:
                try:
                    contract_html = ""
                    for c in contracts:
                        days_left = (c.end_date - today).days
                        contract_html += f'<tr><td style="padding:8px;border-bottom:1px solid #eee;">{c.title}</td><td style="padding:8px;border-bottom:1px solid #eee;">{c.contract_no}</td><td style="padding:8px;border-bottom:1px solid #eee;">{c.end_date}</td><td style="padding:8px;border-bottom:1px solid #eee;">剩 {days_left} 天</td></tr>'
                    email_body = f'<html><body><h3>合同到期提醒</h3><p>以下合同将在 {remind_days} 天内到期，请及时处理：</p><table style="border-collapse:collapse;width:100%;"><thead><tr><th>合同名称</th><th>合同编号</th><th>到期日期</th><th>剩余天数</th></tr></thead><tbody>{contract_html}</tbody></table></body></html>'
                    send_email(email, title, email_body, db)
                    results["email"] += 1
                except Exception as e:
                    results["errors"].append(f"邮件发送失败({email}): {str(e)}")
    except Exception as e:
        results["errors"].append(f"邮件配置异常: {str(e)}")
    
    # 2. 企业微信通知
    try:
        webhook_url = get_wechat_webhook_url(db)
        if webhook_url:
            wechat_content = f"## 合同到期提醒\n以下合同将在 {remind_days} 天内到期，请及时处理：\n\n" + "\n".join(contract_lines)
            send_wechat_message(webhook_url, wechat_content)
            results["wechat"] = True
    except Exception as e:
        results["errors"].append(f"企业微信发送失败: {str(e)}")
    
    # 3. Server酱通知（所有配置的 SendKey）
    try:
        keys = get_serverchan_keys(db)
        for key in keys:
            try:
                send_serverchan(key, title, content)
                results["serverchan"] += 1
            except Exception as e:
                results["errors"].append(f"Server酱发送失败({key[:8]}...): {str(e)}")
    except Exception as e:
        results["errors"].append(f"Server酱配置异常: {str(e)}")
    
    # 记录通知日志
    for c in contracts:
        for channel in ["email", "wechat", "serverchan"]:
            db.add(Notification(contract_id=c.id, recipient=f"auto:{channel}"))
    db.commit()
    
    return results

# ========== 认证接口 ==========
@app.post("/api/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not pwd_context.verify(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已禁用")
    token = create_token(user.id, user.username)
    return {"access_token": token, "token_type": "bearer",
            "role": user.role, "username": user.username}

@app.post("/api/auth/logout")
def logout(token: str = Depends(oauth2_scheme)):
    _token_blacklist.add(token)
    return {"msg": "已退出登录"}

@app.get("/api/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username,
            "email": current_user.email, "role": current_user.role}

# ========== 用户管理接口 ==========
@app.get("/api/users/")
def list_users(skip: int = 0, limit: int = 20, keyword: str = "",
               db: Session = Depends(get_db), _: User = Depends(require_admin)):
    q = db.query(User)
    if keyword:
        q = q.filter(User.username.ilike(f"%{keyword}%") | User.email.ilike(f"%{keyword}%"))
    total = q.count()
    users = q.offset(skip).limit(limit).all()
    return {"total": total, "items": [
        {"id": u.id, "username": u.username, "email": u.email,
         "role": u.role, "is_active": u.is_active} for u in users]}

@app.post("/api/users/")
def create_user(body: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(username=body.username, email=body.email,
                hashed_password=pwd_context.hash(body.password), role=body.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username}

@app.put("/api/users/{user_id}")
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if body.email: user.email = body.email
    if body.role: user.role = body.role
    if body.is_active is not None: user.is_active = body.is_active
    if body.password: user.hashed_password = pwd_context.hash(body.password)
    db.commit()
    return {"msg": "更新成功"}

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(user)
    db.commit()
    return {"msg": "删除成功"}

# ========== 合同接口 ==========
@app.get("/api/contracts/stats")
def stats(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    all_c = db.query(Contract).all()
    for c in all_c:
        new_status = calc_status(c)
        if c.status != new_status and c.status != "已终止":
            c.status = new_status
    db.commit()
    total = len(all_c)
    # 生效中 = 执行中 + 即将到期（即将到期是生效中的子集）
    active = sum(1 for c in all_c if c.status in ("执行中", "即将到期"))
    expiring = sum(1 for c in all_c if c.status == "即将到期")
    expired = sum(1 for c in all_c if c.status == "已到期")
    completed = sum(1 for c in all_c if c.status == "已终止")
    
    today = date.today()
    last_month_start = date(today.year, today.month - 1 if today.month > 1 else 12, 1)
    if today.month == 12:
        last_month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        last_month_end = date(today.year, today.month, 1) - timedelta(days=1)
    this_month_start = date(today.year, today.month, 1)
    
    last_month_count = db.query(Contract).filter(
        Contract.sign_date >= last_month_start,
        Contract.sign_date <= last_month_end
    ).count()
    this_month_count = db.query(Contract).filter(
        Contract.sign_date >= this_month_start,
        Contract.sign_date <= today
    ).count()
    
    last_month_stats = db.query(Contract).filter(
        Contract.sign_date <= last_month_end
    ).all()
    last_month_total = len(last_month_stats)
    last_month_active = sum(1 for c in last_month_stats if calc_status(c) in ("执行中", "即将到期"))
    last_month_expiring = sum(1 for c in last_month_stats if calc_status(c) == "即将到期")
    last_month_expired = sum(1 for c in last_month_stats if calc_status(c) == "已到期")
    
    def calc_change(current, prev):
        if prev == 0:
            return 0 if current == 0 else 100
        return ((current - prev) / prev) * 100
    
    return {
        "total": total, "active": active, "expiring": expiring, "expired": expired, "completed": completed,
        "total_change": round(calc_change(total, last_month_total), 1),
        "active_change": round(calc_change(active, last_month_active), 1),
        "expiring_change": round(calc_change(expiring, last_month_expiring), 1),
        "expired_change": round(calc_change(expired, last_month_expired), 1),
        "monthly_change": round(calc_change(this_month_count, last_month_count), 1)
    }

@app.get("/api/contracts/expiring")
def expiring_contracts(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    today = date.today()
    items = db.query(Contract).filter(
        Contract.end_date <= today + timedelta(days=30)
    ).order_by(Contract.end_date).limit(20).all()
    return [contract_dict(c) for c in items]

@app.get("/api/contracts/monthly-trend")
def monthly_trend(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    today = date.today()
    result = []
    for i in range(12):
        month_start = date(today.year, i + 1, 1)
        if i + 1 == 12:
            month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(today.year, i + 2, 1) - timedelta(days=1)
        count = db.query(Contract).filter(
            Contract.sign_date >= month_start,
            Contract.sign_date <= month_end
        ).count()
        result.append({
            "month": i + 1,
            "label": f"{i + 1}月",
            "value": count
        })
    return result

@app.get("/api/contracts/")
def list_contracts(
    skip: int = 0, limit: int = 20,
    keyword: str = "", status: Optional[str] = None,
    contract_type: Optional[str] = None,
    start: Optional[str] = None, end: Optional[str] = None,
    db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    q = db.query(Contract)
    if keyword:
        q = q.filter(Contract.title.ilike(f"%{keyword}%") | Contract.contract_no.ilike(f"%{keyword}%") | Contract.party_a.ilike(f"%{keyword}%"))
    if status:
        if status == "生效中":
            q = q.filter(Contract.status.in_(["执行中", "即将到期"]))
        elif status == "已过期":
            q = q.filter(Contract.status == "已到期")
        else:
            q = q.filter(Contract.status == status)
    if contract_type:
        q = q.filter(Contract.contract_type == contract_type)
    if start:
        q = q.filter(Contract.end_date >= start)
    if end:
        q = q.filter(Contract.end_date <= end)
    total = q.count()
    items = q.order_by(Contract.end_date).offset(skip).limit(limit).all()
    return {"total": total, "items": [contract_dict(c) for c in items]}

def parse_date(date_str: str):
    if not date_str:
        return None
    return datetime.strptime(date_str, "%Y-%m-%d").date()

@app.post("/api/contracts/")
def create_contract(body: ContractCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    if db.query(Contract).filter(Contract.contract_no == body.contract_no).first():
        raise HTTPException(status_code=400, detail="合同编号已存在")
    c = Contract(
        contract_no=body.contract_no, title=body.title,
        party_a=body.party_a, party_b=body.party_b,
        amount=body.amount, contract_type=body.contract_type,
        sign_date=parse_date(body.sign_date),
        start_date=parse_date(body.start_date),
        end_date=parse_date(body.end_date),
        remind_days=body.remind_days,
        remark=body.remark, file_path=body.file_path,
        created_by=current_user.id
    )
    c.status = calc_status(c)
    db.add(c)
    db.commit()
    db.refresh(c)
    return contract_dict(c)

@app.get("/api/contracts/{cid}")
def get_contract(cid: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    c = db.query(Contract).filter(Contract.id == cid).first()
    if not c:
        raise HTTPException(status_code=404, detail="合同不存在")
    return contract_dict(c)

@app.put("/api/contracts/{cid}")
def update_contract(cid: int, body: ContractCreate, db: Session = Depends(get_db),
                    _: User = Depends(get_current_user)):
    c = db.query(Contract).filter(Contract.id == cid).first()
    if not c:
        raise HTTPException(status_code=404, detail="合同不存在")
    data = body.model_dump()
    for k, v in data.items():
        if k in ("sign_date", "start_date", "end_date"):
            v = parse_date(v)
        setattr(c, k, v)
    c.status = calc_status(c)
    db.commit()
    return contract_dict(c)

@app.delete("/api/contracts/{cid}")
def delete_contract(cid: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    c = db.query(Contract).filter(Contract.id == cid).first()
    if not c:
        raise HTTPException(status_code=404, detail="合同不存在")
    db.delete(c)
    db.commit()
    return {"msg": "删除成功"}

# ========== 文件上传接口 ==========
ALLOWED_TYPES = {"application/pdf", "application/msword",
                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_SIZE = 50 * 1024 * 1024

@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...), _: User = Depends(get_current_user)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="只支持PDF和Word文件")
    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过50MB")
    ext = file.filename.rsplit(".", 1)[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(data)
    return {"file_path": filename, "original_name": file.filename}

def get_user_from_token(token: str, db: Session):
    if token in _token_blacklist:
        raise HTTPException(status_code=401, detail="Token已失效")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user = db.query(User).filter(User.id == int(payload["sub"])).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="用户不存在或已禁用")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token无效")

def _get_token_user(token: Optional[str], db: Session):
    """通用token认证：优先从URL参数获取，再从Header获取"""
    if token:
        return get_user_from_token(token, db)
    raise HTTPException(status_code=401, detail="缺少认证token")

@app.get("/api/files/download/{filename}")
def download_file(filename: str, token: Optional[str] = None, db: Session = Depends(get_db)):
    _get_token_user(token, db)
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="文件不存在")
    # 根据扩展名设置media_type
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    media_types = {
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    media_type = media_types.get(ext, "application/octet-stream")
    return FileResponse(filepath, filename=filename, media_type=media_type)

@app.get("/api/files/preview/{filename}")
def preview_file(filename: str, token: Optional[str] = None, db: Session = Depends(get_db)):
    _get_token_user(token, db)
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="文件不存在")
    # 根据扩展名设置media_type
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    media_types = {
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    media_type = media_types.get(ext, "application/octet-stream")
    # 不传filename参数，使Content-Disposition为inline，浏览器内联显示而非下载
    return FileResponse(filepath, media_type=media_type)

# ========== 健康检查 ==========
@app.get("/api/health")
def health():
    return {"status": "ok"}

# ========== 邮件配置接口 ==========
@app.get("/api/settings/smtp")
def get_smtp_settings(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """获取 SMTP 配置（密码返回掩码）"""
    cfg = get_smtp_config(db)
    return {
        "smtp_host": cfg["host"],
        "smtp_port": cfg["port"],
        "smtp_user": cfg["user"],
        "smtp_password": "******" if cfg["password"] else "",
        "configured": bool(cfg["host"] and cfg["user"] and cfg["password"])
    }

@app.put("/api/settings/smtp")
def save_smtp_settings(body: SmtpConfig, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """保存 SMTP 配置"""
    settings_map = {
        "smtp_host": body.smtp_host,
        "smtp_port": str(body.smtp_port),
        "smtp_user": body.smtp_user,
    }
    # 密码不为空且不是掩码时才更新
    if body.smtp_password and body.smtp_password != "******":
        settings_map["smtp_password"] = body.smtp_password
    
    for key, value in settings_map.items():
        existing = db.query(Setting).filter(Setting.key == key).first()
        if existing:
            existing.value = value
        else:
            db.add(Setting(key=key, value=value))
    db.commit()
    return {"message": "配置保存成功"}

@app.post("/api/settings/smtp/test")
def test_smtp_settings(body: TestEmail, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """发送测试邮件"""
    test_body = """
    <html><body>
    <h3>测试邮件</h3>
    <p>恭喜！您的合同管理系统邮件配置已成功生效。</p>
    <p style="color:#94a3b8;font-size:12px;">此邮件由合同管理系统发送</p>
    </body></html>
    """
    send_email(body.to_email, "【合同管理系统】测试邮件", test_body, db)
    return {"message": "测试邮件发送成功"}

@app.get("/api/settings/wechat")
def get_wechat_settings(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """获取企业微信 Webhook 配置"""
    webhook_url = get_wechat_webhook_url(db)
    return {
        "wechat_webhook_url": webhook_url,
        "configured": bool(webhook_url)
    }

@app.put("/api/settings/wechat")
def save_wechat_settings(body: WechatConfig, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """保存企业微信 Webhook 配置"""
    existing = db.query(Setting).filter(Setting.key == "wechat_webhook_url").first()
    if existing:
        existing.value = body.wechat_webhook_url
    else:
        db.add(Setting(key="wechat_webhook_url", value=body.wechat_webhook_url))
    db.commit()
    return {"message": "配置保存成功"}

@app.post("/api/settings/wechat/test")
def test_wechat_settings(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """发送测试企业微信消息"""
    webhook_url = get_wechat_webhook_url(db)
    if not webhook_url:
        raise HTTPException(status_code=400, detail="企业微信 Webhook 未配置")
    
    test_content = """## 测试消息
恭喜！您的合同管理系统企业微信配置已成功生效。

---
*此消息由合同管理系统自动发送*"""
    
    send_wechat_message(webhook_url, test_content)
    return {"message": "测试消息发送成功"}

# ========== Server酱配置接口 ==========
@app.get("/api/settings/serverchan")
def get_serverchan_settings(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """获取 Server酱 配置"""
    keys = get_serverchan_keys(db)
    return {
        "serverchan_keys": "\n".join(keys),
        "key_count": len(keys),
        "configured": len(keys) > 0
    }

@app.put("/api/settings/serverchan")
def save_serverchan_settings(body: ServerChanConfig, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """保存 Server酱 配置"""
    set_setting(db, "serverchan_keys", body.serverchan_keys)
    db.commit()
    return {"message": "配置保存成功"}

@app.post("/api/settings/serverchan/test")
def test_serverchan_settings(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """发送测试 Server酱 消息"""
    keys = get_serverchan_keys(db)
    if not keys:
        raise HTTPException(status_code=400, detail="Server酱 SendKey 未配置")
    
    errors = []
    success = 0
    for key in keys:
        try:
            send_serverchan(key, "【合同管理系统】测试消息", "恭喜！Server酱配置已成功生效，您将收到合同到期提醒通知。")
            success += 1
        except Exception as e:
            errors.append(f"{key[:8]}...: {str(e)}")
    
    if success > 0:
        return {"message": f"测试消息发送成功（{success}/{len(keys)}）", "errors": errors}
    else:
        raise HTTPException(status_code=500, detail=f"发送失败: {errors[0] if errors else '未知错误'}")

# ========== 自动提醒配置接口 ==========
@app.get("/api/settings/auto-remind")
def get_auto_remind_settings(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """获取自动提醒配置"""
    return {
        "enabled": get_setting(db, "auto_remind_enabled") == "true",
        "remind_days": int(get_setting(db, "auto_remind_days", "30")),
        "last_run": str(_last_remind_date) if _last_remind_date else None
    }

@app.put("/api/settings/auto-remind")
def save_auto_remind_settings(body: AutoRemindConfig, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """保存自动提醒配置"""
    set_setting(db, "auto_remind_enabled", "true" if body.auto_remind_enabled else "false")
    set_setting(db, "auto_remind_days", str(body.auto_remind_days))
    db.commit()
    return {"message": "配置保存成功"}

@app.post("/api/notifications/auto-remind/trigger")
def trigger_auto_remind(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """手动触发一次自动提醒"""
    global _last_remind_date
    result = do_auto_remind(db)
    _last_remind_date = date.today()
    return {
        "message": "手动提醒已执行",
        "result": result
    }

# ========== 通知接口 ==========
@app.get("/api/notifications/pending-contracts")
def pending_contracts(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    today = date.today()
    items = db.query(Contract).filter(
        Contract.end_date <= today + timedelta(days=60),
        Contract.status != "已终止"
    ).order_by(Contract.end_date).all()
    return [contract_dict(c) for c in items]

@app.post("/api/notifications/send")
def send_notification(body: NotificationSend, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    contracts = db.query(Contract).filter(Contract.id.in_(body.contract_ids)).all()
    if not contracts:
        raise HTTPException(status_code=400, detail="未找到指定的合同")
    
    success_count = 0
    failed_count = 0
    failed_emails = []
    wechat_success = False
    wechat_error = None
    serverchan_success = 0
    serverchan_errors = []
    
    # 如果没有指定合同ID，自动查找快到期的合同
    if not body.contract_ids:
        today = date.today()
        remind_days = int(get_setting(db, "auto_remind_days", "30"))
        deadline = today + timedelta(days=remind_days)
        contracts = db.query(Contract).filter(
            Contract.end_date <= deadline,
            Contract.end_date >= today,
            Contract.status != "已终止"
        ).order_by(Contract.end_date).all()
        if not contracts:
            return {"success": 0, "failed": 0, "message": "当前无需提醒的合同", "wechat_success": False, "wechat_error": None, "serverchan_success": 0, "serverchan_errors": []}
    
    # 发送邮件通知
    for email in body.to_emails:
        if not email:
            continue
        try:
            contract_list = ""
            for c in contracts:
                days_left = (c.end_date - date.today()).days
                status_text = f"还剩 {days_left} 天到期" if days_left > 0 else "已过期"
                contract_list += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{c.title}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{c.contract_no}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{c.end_date}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{status_text}</td>
                </tr>
                """
            
            default_message = "以下合同即将到期，请及时处理："
            custom_message = body.message if body.message else default_message
            
            email_body = f"""
            <html>
            <head>
                <style>
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ text-align: left; padding: 12px; }}
                    th {{ background: #f8fafc; }}
                </style>
            </head>
            <body>
                <h3 style="color: #1e293b;">合同到期提醒</h3>
                <p style="color: #475569; line-height: 1.6;">{custom_message}</p>
                <table style="margin-top: 16px;">
                    <thead>
                        <tr>
                            <th>合同名称</th>
                            <th>合同编号</th>
                            <th>到期日期</th>
                            <th>状态</th>
                        </tr>
                    </thead>
                    <tbody>
                        {contract_list}
                    </tbody>
                </table>
                <p style="color: #94a3b8; font-size: 12px; margin-top: 20px;">此邮件由合同管理系统自动发送</p>
            </body>
            </html>
            """
            
            send_email(email, "【合同到期提醒】", email_body, db)
            success_count += 1
        except Exception as e:
            failed_count += 1
            failed_emails.append({"email": email, "error": str(e)})
    
    # 发送企业微信通知
    if body.send_wechat:
        try:
            webhook_url = get_wechat_webhook_url(db)
            if not webhook_url:
                wechat_error = "企业微信 Webhook 未配置"
            else:
                # 构建 Markdown 格式消息
                contract_lines = []
                for c in contracts:
                    days_left = (c.end_date - date.today()).days
                    status_text = f"还剩 {days_left} 天" if days_left > 0 else "**已过期**"
                    contract_lines.append(f"> {c.title}（{c.contract_no}）\n> 到期：{c.end_date} | {status_text}")
                
                custom_message = body.message if body.message else "以下合同即将到期，请及时处理："
                wechat_content = f"""## 合同到期提醒
{custom_message}

{chr(10).join(contract_lines)}

---
*此消息由合同管理系统自动发送*"""
                
                send_wechat_message(webhook_url, wechat_content)
                wechat_success = True
        except Exception as e:
            wechat_error = str(e)
    
    # 发送 Server酱 通知
    if body.send_serverchan:
        try:
            keys = get_serverchan_keys(db)
            if not keys:
                serverchan_errors.append("Server酱 SendKey 未配置")
            else:
                contract_lines = []
                for c in contracts:
                    days_left = (c.end_date - date.today()).days
                    status_text = f"剩 {days_left} 天" if days_left > 0 else "已过期"
                    contract_lines.append(f"- {c.title}（{c.contract_no}）\n  到期：{c.end_date} | {status_text}")
                
                custom_message = body.message if body.message else "以下合同即将到期，请及时处理："
                sc_title = f"【合同到期提醒】{len(contracts)}个合同即将到期"
                sc_content = f"{custom_message}\n\n" + "\n".join(contract_lines)
                
                for key in keys:
                    try:
                        send_serverchan(key, sc_title, sc_content)
                        serverchan_success += 1
                    except Exception as e:
                        serverchan_errors.append(f"{key[:8]}...: {str(e)}")
        except Exception as e:
            serverchan_errors.append(str(e))
    
    return {
        "success": success_count,
        "failed": failed_count,
        "failed_emails": failed_emails,
        "wechat_success": wechat_success,
        "wechat_error": wechat_error,
        "serverchan_success": serverchan_success,
        "serverchan_errors": serverchan_errors
    }

# ========== 静态文件（前端 SPA） ==========
from starlette.responses import FileResponse as StarletteFileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
INDEX_FILE = os.path.join(STATIC_DIR, "index.html")

class SPAMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 404 and not request.url.path.startswith("/api"):
            if os.path.exists(INDEX_FILE):
                return StarletteFileResponse(INDEX_FILE)
        return response

app.add_middleware(SPAMiddleware)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")