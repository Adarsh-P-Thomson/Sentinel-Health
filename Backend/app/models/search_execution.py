"""
SearchExecution SQLAlchemy model
"""
from sqlalchemy import Column, String, Integer, TIMESTAMP, ARRAY, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class SearchExecution(Base):
    """Search execution tracking model"""
    
    __tablename__ = "search_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)  # Optional for public searches
    source_id = Column(String(100), nullable=False)  # Source identifier like 'reddit', 'twitter', not UUID
    
    # Search parameters
    search_query = Column(Text, nullable=False)
    keywords_used = Column(ARRAY(Text))
    
    # Execution metadata
    search_type = Column(String(50), nullable=False)  # keyword_search, url_crawl, api_fetch
    status = Column(String(50), default="pending")  # pending, running, completed, failed, partial
    
    # Results tracking
    pages_found = Column(Integer, default=0)
    pages_stored = Column(Integer, default=0)
    posts_extracted = Column(Integer, default=0)
    
    # MongoDB references
    mongodb_page_ids = Column(ARRAY(Text))
    mongodb_post_ids = Column(ARRAY(Text))
    
    # Timing
    started_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(TIMESTAMP)
    duration_ms = Column(Integer)
    
    # Error tracking
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Next execution
    next_scheduled_at = Column(TIMESTAMP)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
