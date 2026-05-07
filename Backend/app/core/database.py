"""
Database connection management for PostgreSQL and MongoDB
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# ============================================================================
# PostgreSQL Setup
# ============================================================================

# Convert postgresql:// to postgresql+asyncpg://
ASYNC_DATABASE_URL = settings.database_url.replace(
    "postgresql://",
    "postgresql+asyncpg://"
)

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.debug,
    pool_size=settings.postgres_pool_size,
    max_overflow=settings.postgres_max_overflow,
    pool_pre_ping=True,  # Verify connections before using
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for SQLAlchemy models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions
    
    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ============================================================================
# MongoDB Setup
# ============================================================================

class MongoDB:
    """MongoDB connection manager"""
    
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect(cls):
        """Connect to MongoDB"""
        mongodb_url = settings.get_mongodb_url()
        print(f"🔗 Connecting to MongoDB: {mongodb_url.replace(settings.mongodb_password or '', '***') if settings.mongodb_password else mongodb_url}")
        
        cls.client = AsyncIOMotorClient(
            mongodb_url,
            maxPoolSize=settings.mongodb_max_pool_size,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
        )
        
        # Verify connection
        await cls.client.admin.command('ping')
        print(f"✓ Connected to MongoDB: {settings.mongodb_db}")
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB"""
        if cls.client:
            cls.client.close()
            print("✓ Disconnected from MongoDB")
    
    @classmethod
    def get_database(cls):
        """Get MongoDB database instance"""
        if not cls.client:
            raise RuntimeError("MongoDB client not initialized. Call connect() first.")
        return cls.client[settings.mongodb_db]
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Get MongoDB collection"""
        db = cls.get_database()
        return db[collection_name]


# Convenience function for getting MongoDB database
def get_mongodb():
    """
    Dependency for getting MongoDB database
    
    Usage:
        @app.get("/posts")
        async def get_posts(db = Depends(get_mongodb)):
            collection = db["raw_posts"]
            ...
    """
    return MongoDB.get_database()
