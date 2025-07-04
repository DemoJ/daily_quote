"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime, date
from app.database import Base


class DailyQuote(Base):
    """每日语录模型"""
    __tablename__ = "daily_quotes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False, comment="语录内容")
    author = Column(String(100), default="AI智慧", comment="作者")
    date = Column(String(10), nullable=False, unique=True, index=True, comment="日期(YYYY-MM-DD)")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    is_ai_generated = Column(Boolean, default=True, comment="是否AI生成")
    generation_attempts = Column(Integer, default=1, comment="生成尝试次数")
    is_fallback = Column(Boolean, default=False, comment="是否为兜底语录")

    def __repr__(self):
        return f"<DailyQuote(id={self.id}, date={self.date}, content='{self.content[:50]}...')>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "content": self.content,
            "author": self.author,
            "date": self.date,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_ai_generated": self.is_ai_generated,
            "generation_attempts": self.generation_attempts,
            "is_fallback": self.is_fallback
        }


class QuoteGenerationLog(Base):
    """语录生成日志模型"""
    __tablename__ = "quote_generation_logs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), nullable=False, index=True, comment="目标日期")
    attempt_number = Column(Integer, nullable=False, comment="尝试次数")
    success = Column(Boolean, nullable=False, comment="是否成功")
    error_message = Column(Text, comment="错误信息")
    generated_content = Column(Text, comment="生成的内容")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<QuoteGenerationLog(id={self.id}, date={self.date}, attempt={self.attempt_number}, success={self.success})>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "date": self.date,
            "attempt_number": self.attempt_number,
            "success": self.success,
            "error_message": self.error_message,
            "generated_content": self.generated_content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
