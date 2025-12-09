#!/usr/bin/env python3
"""
Script para inicializar o banco de dados.
Cria todas as tabelas definidas nos models SQLAlchemy.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from src.db.models import Base
from src.config.settings import get_settings

settings = get_settings()


async def init_database():
    """Create all tables in the database."""
    print(f"Connecting to database: {settings.DATABASE_URL}")

    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)

        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

    print("✅ Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_database())
