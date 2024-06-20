import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler
from tornado.ioloop import IOLoop
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from apps.domain.models import Base
from apps.services.fix_data import DataService
from apps.web import make_app
from config import settings


log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '.', 'logs'))
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'main.log')
logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5),  # 10 MB per file, keep 5 backups
        logging.StreamHandler()  # Also log to console
    ]
)

async_engine = create_async_engine(settings.pgsql, echo=True)
async_session_factory = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

logging.info(settings.as_dict())

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logging.info("Database initialized")


async def main():
    try:
        # Initialize database and get async session factory
        await init_db()
        app = make_app(async_session_factory)
        app.listen(settings.server.port)
        logging.info(f"Listening on port {settings.server.port}")

        # 同步原表的数据
        if settings.data_sync:
            await asyncio.create_task(DataService(async_session_factory).movie())
            await asyncio.create_task(DataService(async_session_factory).tv())

        # Keep the server running
        await asyncio.Event().wait()
    except Exception as e:
        logging.error("Error in main function", exc_info=True)




if __name__ == "__main__":
    try:
        IOLoop.current().run_sync(main)
    except Exception as e:
        logging.error("Error starting the IOLoop", exc_info=True)
