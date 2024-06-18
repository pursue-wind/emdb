# app/main.py

import asyncio
from tornado.ioloop import IOLoop
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from apps.config.config import cfg
from apps.domain.models import Base
from apps.web import make_app

async_engine = create_async_engine(cfg.pgsql, echo=True)
async_session_factory = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    # Initialize database and get async session factory
    await init_db()
    app = make_app(async_session_factory)
    app.listen(cfg.server.port)
    print(f"Listening on port {cfg.PORT}")

    await asyncio.Event().wait()

if __name__ == "__main__":
    IOLoop.current().run_sync(main)
