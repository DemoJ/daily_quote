"""
每日一言系统主应用
"""
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 导入应用模块
from app.api import router as api_router
from app.database import create_tables_async
from app.scheduler import quote_scheduler

# 加载环境变量
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 启动每日一言系统...")
    
    # 创建数据库表
    await create_tables_async()
    print("✅ 数据库初始化完成")
    
    # 启动定时任务调度器
    await quote_scheduler.start()
    print("✅ 定时任务调度器启动完成")
    
    print("🎉 每日一言系统启动成功！")
    
    yield
    
    # 关闭时执行
    print("🛑 正在关闭每日一言系统...")
    await quote_scheduler.stop()
    print("✅ 系统关闭完成")


# 创建FastAPI应用
app = FastAPI(
    title="每日一言系统 API",
    description="专注于提供高质量哲学家名言的API服务，支持获取真实哲学家的深度语录",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件（仅开发环境）
debug_mode = os.getenv("DEBUG", "False").lower() == "true"

if debug_mode:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 开发环境允许所有来源
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("🔓 开发模式：已启用CORS跨域支持")
else:
    print("🔒 生产模式：CORS跨域支持已禁用")

# 注册API路由
app.include_router(api_router, prefix="/api", tags=["API"])


@app.get("/", summary="API信息", description="获取API基本信息和使用说明")
async def api_info():
    """API信息页面"""
    return {
        "service": "每日一言系统 API",
        "version": "1.0.0",
        "description": "专注于提供高质量哲学家名言的API服务",
        "features": [
            "真实哲学家名言",
            "30字以上深度语录",
            "自动定时生成",
            "多种查询方式"
        ],
        "endpoints": {
            "获取今日语录": "GET /api/quote",
            "获取指定日期语录": "GET /api/quote/{date}",
            "获取最近语录": "GET /api/quotes/recent",
            "系统健康检查": "GET /health",
            "API文档": "GET /docs",
            "OpenAPI规范": "GET /openapi.json"
        },
        "usage_example": {
            "curl": "curl http://localhost:8000/api/quote",
            "response": {
                "success": True,
                "data": {
                    "content": "示例哲学家名言...",
                    "author": "哲学家姓名",
                    "date": "2025-07-03"
                }
            }
        },
        "documentation": "访问 /docs 查看完整的API文档",
        "note": "本服务专注于API功能，前端页面已独立为可选组件"
    }


@app.get("/health", summary="系统健康检查")
async def system_health():
    """系统健康检查"""
    scheduler_status = quote_scheduler.get_scheduler_status()
    
    return {
        "status": "healthy",
        "service": "每日一言系统",
        "version": "1.0.0",
        "scheduler": scheduler_status,
        "database": "connected"
    }


@app.get("/admin/scheduler", summary="调度器状态", description="获取定时任务调度器状态")
async def get_scheduler_status():
    """获取调度器状态"""
    return quote_scheduler.get_scheduler_status()


@app.post("/admin/generate", summary="手动生成语录", description="手动触发生成指定日期的语录。注意：此接口可通过环境变量ENABLE_MANUAL_GENERATION控制是否启用。")
async def manual_generate(target_date: str):
    """手动生成语录"""
    # 检查是否启用手动生成功能
    enable_manual_generation = os.getenv("ENABLE_MANUAL_GENERATION", "False").lower() == "true"

    if not enable_manual_generation:
        return {
            "success": False,
            "message": "手动生成功能已被禁用。如需启用，请在.env文件中设置ENABLE_MANUAL_GENERATION=True"
        }

    result = await quote_scheduler.manual_generate_quote(target_date)
    return result


if __name__ == "__main__":
    # 从环境变量获取配置
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                        每日一言系统                          ║
║                    Daily Quote System                        ║
╠══════════════════════════════════════════════════════════════╣
║  🌟 功能特性:                                                ║
║     • API接口: 通过URL获取每日语录                           ║
║     • 前端展示: 美观极简的日签预览页面                       ║
║     • AI生成: 使用OpenAI兼容的LLM生成高质量语录              ║
║     • 定时更新: 每日23:00自动生成下一日语录                  ║
║     • 重试机制: 失败时自动重试3次                            ║
║     • 兜底机制: 异常时从历史语录中随机选择                   ║
║                                                              ║
║  🔗 访问地址:                                                ║
║     • 前端页面: http://{host}:{port}                         ║
║     • API文档: http://{host}:{port}/docs                     ║
║     • 健康检查: http://{host}:{port}/health                  ║
║                                                              ║
║  📚 API接口:                                                 ║
║     • GET /api/quote - 获取今日语录                          ║
║     • GET /api/quote/{{date}} - 获取指定日期语录             ║
║     • GET /api/quotes/recent - 获取最近语录                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 检查必要的环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未设置 OPENAI_API_KEY 环境变量")
        print("   请在 .env 文件中配置您的 OpenAI API Key")
        print("   示例: OPENAI_API_KEY=your_api_key_here")
        print()
    
    # 启动应用
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )
