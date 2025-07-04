"""
定时任务调度器
"""
import os
from datetime import datetime, date, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.ai_service import ai_service
from app.database import create_tables_async
import logging

logger = logging.getLogger(__name__)


class QuoteScheduler:
    """语录定时任务调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
        # 从环境变量获取定时任务配置
        self.generation_hour = int(os.getenv("QUOTE_GENERATION_HOUR", "23"))
        self.generation_minute = int(os.getenv("QUOTE_GENERATION_MINUTE", "0"))
    
    async def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("调度器已经在运行中")
            return
        
        try:
            # 确保数据库表已创建
            await create_tables_async()
            
            # 添加定时任务：每日23:00生成下一日语录
            self.scheduler.add_job(
                self.generate_next_day_quote,
                CronTrigger(hour=self.generation_hour, minute=self.generation_minute),
                id="daily_quote_generation",
                name="每日语录生成任务",
                replace_existing=True
            )
            
            # 添加启动时的初始化任务
            self.scheduler.add_job(
                self.initialize_today_quote,
                "date",
                run_date=datetime.now(),
                id="initialize_today_quote",
                name="初始化今日语录"
            )
            
            # 启动调度器
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"定时任务调度器已启动，每日 {self.generation_hour:02d}:{self.generation_minute:02d} 生成下一日语录")
            
        except Exception as e:
            logger.error(f"启动调度器失败: {e}")
            raise e
    
    async def stop(self):
        """停止调度器"""
        if not self.is_running:
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("定时任务调度器已停止")
        except Exception as e:
            logger.error(f"停止调度器失败: {e}")
    
    async def initialize_today_quote(self):
        """初始化今日语录（如果不存在）"""
        try:
            # 检查是否配置了API密钥
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key or api_key == "your_openai_api_key_here":
                logger.warning("未配置OpenAI API Key，跳过今日语录初始化")
                return

            today = date.today().strftime("%Y-%m-%d")
            logger.info(f"检查并初始化今日语录: {today}")

            # 检查今日语录是否存在
            today_quote = await ai_service.get_today_quote()

            if today_quote:
                logger.info(f"今日语录已存在: {today_quote['content'][:50]}...")
            else:
                logger.info("今日语录不存在，开始生成...")
                result = await ai_service.generate_daily_quote(today)

                if result["success"]:
                    logger.info(f"成功生成今日语录: {result['quote']['content'][:50]}...")
                else:
                    logger.error(f"生成今日语录失败: {result.get('message', '未知错误')}")

        except Exception as e:
            logger.error(f"初始化今日语录失败: {e}")
    
    async def generate_next_day_quote(self):
        """生成下一日语录的定时任务"""
        try:
            # 计算下一日日期
            tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            logger.info(f"开始生成下一日语录: {tomorrow}")
            
            # 生成下一日语录
            result = await ai_service.generate_daily_quote(tomorrow)
            
            if result["success"]:
                quote_content = result["quote"]["content"]
                logger.info(f"成功生成 {tomorrow} 的语录: {quote_content[:50]}...")
                
                # 可以在这里添加通知逻辑，比如发送邮件、推送消息等
                await self._notify_generation_success(tomorrow, quote_content)
                
            else:
                error_msg = result.get("message", "未知错误")
                logger.error(f"生成 {tomorrow} 的语录失败: {error_msg}")
                
                # 可以在这里添加错误通知逻辑
                await self._notify_generation_failure(tomorrow, error_msg)
                
        except Exception as e:
            logger.error(f"定时生成语录任务执行失败: {e}")
            await self._notify_generation_failure("未知日期", str(e))
    
    async def _notify_generation_success(self, date_str: str, content: str):
        """通知语录生成成功"""
        # 这里可以实现各种通知方式：邮件、短信、Webhook等
        logger.info(f"语录生成成功通知 - 日期: {date_str}, 内容: {content[:30]}...")
        
        # 示例：可以添加Webhook通知
        # await self._send_webhook_notification({
        #     "type": "success",
        #     "date": date_str,
        #     "content": content,
        #     "timestamp": datetime.now().isoformat()
        # })
    
    async def _notify_generation_failure(self, date_str: str, error_msg: str):
        """通知语录生成失败"""
        # 这里可以实现各种通知方式：邮件、短信、Webhook等
        logger.error(f"语录生成失败通知 - 日期: {date_str}, 错误: {error_msg}")
        
        # 示例：可以添加Webhook通知
        # await self._send_webhook_notification({
        #     "type": "error",
        #     "date": date_str,
        #     "error": error_msg,
        #     "timestamp": datetime.now().isoformat()
        # })
    
    async def manual_generate_quote(self, target_date: str):
        """手动触发生成指定日期的语录"""
        try:
            logger.info(f"手动触发生成语录: {target_date}")
            result = await ai_service.generate_daily_quote(target_date)
            
            if result["success"]:
                logger.info(f"手动生成 {target_date} 的语录成功")
                return result
            else:
                logger.error(f"手动生成 {target_date} 的语录失败: {result.get('message', '未知错误')}")
                return result
                
        except Exception as e:
            logger.error(f"手动生成语录失败: {e}")
            return {
                "success": False,
                "message": f"手动生成失败: {str(e)}"
            }
    
    def get_scheduler_status(self):
        """获取调度器状态"""
        jobs = []
        if self.is_running:
            for job in self.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                })
        
        return {
            "is_running": self.is_running,
            "jobs": jobs,
            "generation_time": f"{self.generation_hour:02d}:{self.generation_minute:02d}"
        }


# 创建全局调度器实例
quote_scheduler = QuoteScheduler()
