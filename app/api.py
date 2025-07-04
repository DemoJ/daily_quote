"""
FastAPI路由和API接口
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from datetime import date, datetime
from typing import Optional, Dict, Any
from app.database import get_async_db, AsyncSessionLocal
from app.models import DailyQuote
from app.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

# 创建API路由器
router = APIRouter()


@router.get("/quote", summary="获取每日语录", description="获取当天的每日语录")
async def get_daily_quote():
    """
    获取每日语录
    
    Returns:
        Dict: 包含语录信息的字典
    """
    try:
        quote_data = await ai_service.get_today_quote()
        
        if not quote_data:
            raise HTTPException(
                status_code=500, 
                detail="无法获取今日语录，请稍后重试"
            )
        
        return {
            "success": True,
            "data": quote_data,
            "message": "获取成功"
        }
        
    except Exception as e:
        logger.error(f"获取每日语录失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )


@router.get("/quote/{target_date}", summary="获取指定日期语录", description="获取指定日期的语录")
async def get_quote_by_date(target_date: str):
    """
    获取指定日期的语录
    
    Args:
        target_date: 日期字符串 (YYYY-MM-DD)
        
    Returns:
        Dict: 包含语录信息的字典
    """
    try:
        # 验证日期格式
        try:
            datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="日期格式错误，请使用 YYYY-MM-DD 格式"
            )
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(DailyQuote).where(DailyQuote.date == target_date)
            )
            quote = result.scalar_one_or_none()
            
            if not quote:
                raise HTTPException(
                    status_code=404,
                    detail=f"未找到日期 {target_date} 的语录"
                )
            
            return {
                "success": True,
                "data": quote.to_dict(),
                "message": "获取成功"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取指定日期语录失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )


@router.get("/quotes/recent", summary="获取最近的语录", description="获取最近N条语录")
async def get_recent_quotes(limit: int = 10):
    """
    获取最近的语录列表
    
    Args:
        limit: 返回的语录数量，默认10条，最大50条
        
    Returns:
        Dict: 包含语录列表的字典
    """
    try:
        # 限制查询数量
        if limit > 50:
            limit = 50
        elif limit < 1:
            limit = 1
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(DailyQuote)
                .order_by(desc(DailyQuote.date))
                .limit(limit)
            )
            quotes = result.scalars().all()
            
            quotes_data = [quote.to_dict() for quote in quotes]
            
            return {
                "success": True,
                "data": quotes_data,
                "count": len(quotes_data),
                "message": "获取成功"
            }
            
    except Exception as e:
        logger.error(f"获取最近语录失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )


@router.post("/quote/generate", summary="手动生成语录", description="手动为指定日期生成语录")
async def generate_quote_manually(target_date: str):
    """
    手动生成指定日期的语录
    
    Args:
        target_date: 目标日期 (YYYY-MM-DD)
        
    Returns:
        Dict: 生成结果
    """
    try:
        # 验证日期格式
        try:
            datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="日期格式错误，请使用 YYYY-MM-DD 格式"
            )
        
        # 检查是否已存在
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(DailyQuote).where(DailyQuote.date == target_date)
            )
            existing_quote = result.scalar_one_or_none()
            
            if existing_quote:
                return {
                    "success": True,
                    "data": existing_quote.to_dict(),
                    "message": "该日期的语录已存在"
                }
        
        # 生成新语录
        result = await ai_service.generate_daily_quote(target_date)
        
        if result["success"]:
            return {
                "success": True,
                "data": result["quote"],
                "message": f"成功生成 {target_date} 的语录"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"生成语录失败: {result.get('message', '未知错误')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"手动生成语录失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )


@router.get("/health", summary="健康检查", description="检查服务状态")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "每日一言系统"
    }
