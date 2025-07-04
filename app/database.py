"""
数据库配置和连接管理
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./daily_quotes.db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")

# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# 创建基础模型类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


def create_tables():
    """创建数据库表"""
    Base.metadata.create_all(bind=engine)


async def create_tables_async():
    """异步创建数据库表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
