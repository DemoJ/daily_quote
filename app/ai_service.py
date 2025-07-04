"""
AI语录生成服务
"""
import os
import random
import asyncio
from datetime import date
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIQuoteService:
    """AI语录生成服务类"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_retries = 3
        
    async def generate_quote_content(self, target_date: str) -> str:
        """
        使用AI生成语录内容
        
        Args:
            target_date: 目标日期 (YYYY-MM-DD)
            
        Returns:
            生成的语录内容
        """
        # 构建提示词
        prompt = self._build_prompt(target_date)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个哲学名言专家，专门从你的知识库中提取真实哲学家说过的经典名言。你只提供真实存在的、有历史记录的哲学家名言，绝不编造或创作新的内容。请优先选择较长的、具有深刻哲学思辨的语录，避免简短的格言式表达。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            # 清理内容，移除引号等
            content = content.strip('"').strip("'").strip()
            # 移除转义的引号
            content = content.replace('\\"', '"').replace("\\'", "'")

            return content
            
        except Exception as e:
            logger.error(f"AI生成语录失败: {e}")
            raise e
    
    def _build_prompt(self, target_date: str) -> str:
        """构建AI提示词"""

        prompts = [
            "请从你的知识库中提取一句真实哲学家说过的名言。要求：1）必须是历史上真实存在的哲学家说过的话，有历史记录或文献记载；2）内容富有深刻哲理，具有思辨性；3）中文表达，如果原文是外文请提供准确的中文翻译；4）长度必须在30字以上，优先选择50字以上的完整思想表达；5）选择能引发深度思考的完整语录，而非简短格言；6）可以是任何时代、任何文化背景的哲学家；7）返回格式：名言内容|作者姓名。",

            "请提供一句真实哲学家的深刻名言。要求：1）必须是历史上真实存在的哲学家说过或写过的话；2）内容深刻有启发性，具有哲学思辨色彩；3）用中文表达；4）长度必须在30字以上，要有完整的思想表达；5）选择较长的、具有深度思考价值的语录；6）不限制哲学家的时代、国籍或哲学流派；7）返回格式：名言内容|作者姓名。",

            "从世界哲学史上任意一位真实哲学家的言论中选择一句富有哲思的名言。要求：1）必须是有历史记录的真实名言；2）内容具有普世价值和深刻启发意义；3）中文表达；4）长度必须在30字以上，体现完整的哲学思辨；5）优先选择较长的、思想深刻的语录；6）可以是古代、近代或现代的任何哲学家；7）返回格式：名言内容|作者姓名。",

            "请提供一句来自真实哲学家的智慧名言。要求：1）必须是该哲学家真实的言论，有文献记录；2）内容富有智慧，具有深刻的人生哲理或思想洞察；3）使用现代中文表达；4）长度必须在30字以上，要有完整的思想表达；5）选择较长的、适合深度思考的语录；6）不限制哲学家的文化背景或哲学传统；7）返回格式：名言内容|作者姓名。",

            "从人类哲学思想宝库中选择一句真实哲学家的深刻名言。要求：1）必须是该哲学家真实写过或说过的话；2）内容深刻，具有强烈的哲学思辨色彩；3）中文表达；4）长度必须在30字以上，体现完整的思想深度；5）选择能引发关于人生、存在、道德、真理等深层思考的较长语录；6）可以来自任何哲学传统或思想流派；7）返回格式：名言内容|作者姓名。"
        ]

        return random.choice(prompts)

    def _extract_author_from_content(self, content: str) -> str:
        """从AI返回的内容中提取作者信息"""
        try:
            # 检查是否包含 | 分隔符
            if '|' in content:
                parts = content.split('|')
                if len(parts) >= 2:
                    # 返回作者部分
                    author = parts[1].strip()
                    return author

            # 如果没有找到分隔符，尝试从常见格式中提取
            # 格式如：名言内容 —— 作者
            if '——' in content:
                parts = content.split('——')
                if len(parts) >= 2:
                    return parts[1].strip()

            # 格式如：名言内容 - 作者
            if ' - ' in content:
                parts = content.split(' - ')
                if len(parts) >= 2:
                    return parts[1].strip()

            # 如果都没有找到，返回默认值
            return "哲学家"

        except Exception:
            return "哲学家"

    def _clean_quote_content(self, content: str) -> str:
        """清理语录内容，移除作者信息"""
        try:
            # 检查是否包含 | 分隔符
            if '|' in content:
                parts = content.split('|')
                if len(parts) >= 2:
                    cleaned = parts[0].strip()
                else:
                    cleaned = content.strip()
            else:
                cleaned = content.strip()

            # 移除 —— 后面的作者信息
            if '——' in cleaned:
                cleaned = cleaned.split('——')[0].strip()

            # 移除 - 后面的作者信息
            if ' - ' in cleaned:
                cleaned = cleaned.split(' - ')[0].strip()

            # 清理引号
            cleaned = cleaned.strip('"').strip("'").strip()
            # 移除转义的引号
            cleaned = cleaned.replace('\\"', '"').replace("\\'", "'")

            return cleaned

        except Exception:
            return content.strip()

    async def generate_daily_quote(self, target_date: str) -> Dict[str, Any]:
        """
        生成每日语录（包含重试机制）

        Args:
            target_date: 目标日期 (YYYY-MM-DD)

        Returns:
            生成结果字典
        """
        from app.models import DailyQuote
        from app.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            # 检查是否已存在该日期的语录
            existing_quote = await self._get_quote_by_date(db, target_date)
            if existing_quote:
                logger.info(f"日期 {target_date} 的语录已存在")
                return {
                    "success": True,
                    "quote": existing_quote.to_dict(),
                    "message": "语录已存在"
                }
            
            # 尝试生成语录
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info(f"开始第 {attempt} 次尝试生成 {target_date} 的语录")
                    
                    # 生成语录内容
                    raw_content = await self.generate_quote_content(target_date)

                    # 提取作者信息和清理语录内容
                    author = self._extract_author_from_content(raw_content)
                    content = self._clean_quote_content(raw_content)

                    # 保存语录到数据库
                    quote = DailyQuote(
                        content=content,
                        author=author,
                        date=target_date,
                        is_ai_generated=True,
                        generation_attempts=attempt,
                        is_fallback=False
                    )
                    
                    db.add(quote)
                    await db.commit()
                    await db.refresh(quote)
                    
                    # 记录成功日志
                    await self._log_generation_attempt(
                        db, target_date, attempt, True, None, content
                    )
                    
                    logger.info(f"成功生成 {target_date} 的语录")
                    return {
                        "success": True,
                        "quote": quote.to_dict(),
                        "message": f"第 {attempt} 次尝试成功"
                    }
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"第 {attempt} 次尝试失败: {error_msg}")
                    
                    # 记录失败日志
                    await self._log_generation_attempt(
                        db, target_date, attempt, False, error_msg, None
                    )
                    
                    if attempt < self.max_retries:
                        # 等待一段时间后重试
                        await asyncio.sleep(2 ** attempt)  # 指数退避
                    else:
                        # 所有尝试都失败，使用兜底机制
                        logger.warning(f"所有尝试都失败，使用兜底机制为 {target_date} 生成语录")
                        return await self._use_fallback_quote(db, target_date)
            
            # 理论上不会到达这里
            return {
                "success": False,
                "message": "未知错误"
            }

    async def _get_quote_by_date(self, db: Session, target_date: str):
        """根据日期获取语录"""
        from sqlalchemy import select
        from app.models import DailyQuote

        result = await db.execute(
            select(DailyQuote).where(DailyQuote.date == target_date)
        )
        return result.scalar_one_or_none()

    async def _log_generation_attempt(
        self,
        db: Session,
        target_date: str,
        attempt: int,
        success: bool,
        error_msg: Optional[str],
        content: Optional[str]
    ):
        """记录生成尝试日志"""
        from app.models import QuoteGenerationLog

        log = QuoteGenerationLog(
            date=target_date,
            attempt_number=attempt,
            success=success,
            error_message=error_msg,
            generated_content=content
        )
        db.add(log)
        await db.commit()

    async def _use_fallback_quote(self, db: Session, target_date: str) -> Dict[str, Any]:
        """使用兜底机制：从历史语录中随机选择一条"""
        try:
            from sqlalchemy import select
            from app.models import DailyQuote

            # 获取所有历史语录
            result = await db.execute(
                select(DailyQuote).where(DailyQuote.date != target_date)
            )
            historical_quotes = result.scalars().all()

            if not historical_quotes:
                # 如果没有历史语录，使用预设的兜底语录
                fallback_content, fallback_author = self._get_default_fallback_quote()
            else:
                # 随机选择一条历史语录
                selected_quote = random.choice(historical_quotes)
                fallback_content = selected_quote.content
                fallback_author = selected_quote.author

            # 创建兜底语录
            quote = DailyQuote(
                content=fallback_content,
                author=fallback_author,
                date=target_date,
                is_ai_generated=False,
                generation_attempts=self.max_retries,
                is_fallback=True
            )

            db.add(quote)
            await db.commit()
            await db.refresh(quote)

            logger.info(f"为 {target_date} 使用兜底语录")
            return {
                "success": True,
                "quote": quote.to_dict(),
                "message": "使用兜底语录"
            }

        except Exception as e:
            logger.error(f"兜底机制失败: {e}")
            return {
                "success": False,
                "message": f"兜底机制失败: {e}"
            }

    def _get_default_fallback_quote(self) -> tuple:
        """获取默认兜底语录，返回(内容, 作者)"""
        default_quotes = [
            ("未经审视的生活不值得过，因为只有通过理性的反思，我们才能真正理解生命的意义", "苏格拉底"),
            ("我们所看到的世界只是洞穴墙壁上的影子，真正的实在存在于理念的世界中", "柏拉图"),
            ("人生的本质就是痛苦，而痛苦的根源在于我们永不满足的意志和欲望", "叔本华"),
            ("当你凝视深渊时，深渊也在凝视着你。人必须在虚无中创造自己的价值", "尼采"),
            ("有两种东西，我对它们的思考越是深沉和持久，它们在我心灵中唤起的惊奇和敬畏就会日新月异，不断增长，这就是我头上的星空和心中的道德律", "康德"),
            ("人是被抛入这个世界的，但人有选择自己存在方式的自由，这就是人的本质", "萨特"),
            ("吾生也有涯，而知也无涯。以有涯随无涯，殆已！知识虽然无穷，但我们要懂得适可而止", "庄子"),
            ("君子之道，暗然而日章；小人之道，的然而日亡。君子之道，淡而不厌，简而文，温而理", "孔子"),
            ("道生一，一生二，二生三，三生万物。万物负阴而抱阳，冲气以为和", "老子"),
            ("存在先于本质，人首先存在，然后通过自己的选择和行动来定义自己是什么", "萨特"),
            ("理性是人类最高贵的能力，但理性也有其界限，在界限之外是信仰的领域", "康德"),
            ("真正的哲学问题只有一个：自杀。判断生活是否值得经历，这本身就是在回答哲学的根本问题", "加缪"),
            ("人的本质不是抽象的存在于单个人身上，在其现实性上，它是一切社会关系的总和", "马克思"),
            ("我们无法选择我们的出身，但我们可以选择我们成为什么样的人", "萨特"),
            ("哲学的任务不是改变世界，而是解释世界，但解释世界的目的最终还是为了改变世界", "马克思")
        ]
        return random.choice(default_quotes)

    async def get_today_quote(self) -> Optional[Dict[str, Any]]:
        """获取今日语录"""
        from app.database import AsyncSessionLocal

        today = date.today().strftime("%Y-%m-%d")

        async with AsyncSessionLocal() as db:
            quote = await self._get_quote_by_date(db, today)
            if quote:
                return quote.to_dict()
            else:
                # 如果今日语录不存在，立即生成一条
                result = await self.generate_daily_quote(today)
                if result["success"]:
                    return result["quote"]
                return None


# 创建全局AI服务实例
ai_service = AIQuoteService()
