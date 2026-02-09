"""
Test configuration and fixtures.
"""

import asyncio
import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from datetime import datetime

from app.main import app
from app.core.database import get_db, Base
from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.knowledge import KnowledgeItem

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_knowledge_platform.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def db_session():
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session):
    """Create a test client."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user."""
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_token(test_user):
    """Create an access token for the test user."""
    token = create_access_token(test_user.id)
    return token


@pytest_asyncio.fixture
async def test_knowledge_item(db_session, test_user):
    """Create a test knowledge item."""
    item = KnowledgeItem(
        id=str(uuid.uuid4()),
        title="Test Knowledge Item",
        content="This is test content for attachment testing.",
        content_type="markdown",
        author_id=test_user.id,
        is_published=True,
        visibility="private",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    return item


@pytest_asyncio.fixture
async def test_knowledge_item_id(test_knowledge_item):
    """Get the ID of the test knowledge item."""
    return test_knowledge_item.id


@pytest_asyncio.fixture
async def async_client(db_session):
    """Create an async test client with database session."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()