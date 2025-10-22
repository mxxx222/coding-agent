from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import uuid
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/coding_agent")

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_active = Column(DateTime(timezone=True))
    subscription_tier = Column(String(50), default='free')
    cost_limit = Column(Float, default=100.00)
    daily_cost_limit = Column(Float, default=10.00)
    monthly_cost_limit = Column(Float, default=100.00)
    request_rate_limit = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="user", cascade="all, delete-orphan")
    cost_tracking = relationship("CostTracking", back_populates="user", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    language = Column(String(50))
    framework = Column(String(100))
    repository_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    code_analyses = relationship("CodeAnalysis", back_populates="project", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="project", cascade="all, delete-orphan")

class CodeAnalysis(Base):
    __tablename__ = "code_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    file_path = Column(String(500), nullable=False)
    code_hash = Column(String(64), nullable=False)
    language = Column(String(50))
    complexity_score = Column(Integer)
    quality_score = Column(Float)
    line_count = Column(Integer)
    function_count = Column(Integer)
    class_count = Column(Integer)
    analysis_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="code_analyses")
    refactor_suggestions = relationship("RefactorSuggestion", back_populates="code_analysis", cascade="all, delete-orphan")
    test_generations = relationship("TestGeneration", back_populates="code_analysis", cascade="all, delete-orphan")
    code_embeddings = relationship("CodeEmbedding", back_populates="code_analysis", cascade="all, delete-orphan")

class RefactorSuggestion(Base):
    __tablename__ = "refactor_suggestions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code_analysis_id = Column(UUID(as_uuid=True), ForeignKey("code_analyses.id"))
    suggestion_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    current_code = Column(Text)
    suggested_code = Column(Text)
    reasoning = Column(Text)
    line_number = Column(Integer)
    confidence_score = Column(Float)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    applied_at = Column(DateTime(timezone=True))
    
    # Relationships
    code_analysis = relationship("CodeAnalysis", back_populates="refactor_suggestions")

class TestGeneration(Base):
    __tablename__ = "test_generations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code_analysis_id = Column(UUID(as_uuid=True), ForeignKey("code_analyses.id"))
    test_framework = Column(String(50), nullable=False)
    test_type = Column(String(20), nullable=False)
    test_code = Column(Text, nullable=False)
    test_file_path = Column(String(500))
    coverage_estimate = Column(Float)
    test_count = Column(Integer)
    status = Column(String(20), default='generated')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True))
    
    # Relationships
    code_analysis = relationship("CodeAnalysis", back_populates="test_generations")

class Integration(Base):
    __tablename__ = "integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    service_name = Column(String(100), nullable=False)
    service_type = Column(String(50), nullable=False)
    config_data = Column(JSON, nullable=False)
    is_enabled = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="integrations")
    project = relationship("Project", back_populates="integrations")

class CostTracking(Base):
    __tablename__ = "cost_tracking"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    operation_type = Column(String(50), nullable=False)
    tokens_used = Column(Integer)
    cost_amount = Column(Float, nullable=False)
    endpoint = Column(String(100))
    request_data = Column(JSON)
    model_used = Column(String(100))
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cost_tracking")

class CodeEmbedding(Base):
    __tablename__ = "code_embeddings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code_analysis_id = Column(UUID(as_uuid=True), ForeignKey("code_analyses.id"))
    embedding_vector = Column(JSON, nullable=False)  # Store as JSON array
    embedding_model = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    code_analysis = relationship("CodeAnalysis", back_populates="code_embeddings")

class APILog(Base):
    __tablename__ = "api_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    endpoint = Column(String(100), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer)
    request_size_bytes = Column(Integer)
    response_size_bytes = Column(Integer)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserAnalytics(Base):
    __tablename__ = "user_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    requests_count = Column(Integer, default=0)
    total_cost = Column(Float, default=0)
    avg_response_time_ms = Column(Integer)
    most_used_endpoint = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ProjectAnalytics(Base):
    __tablename__ = "project_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    analysis_count = Column(Integer, default=0)
    refactor_suggestions_count = Column(Integer, default=0)
    test_generations_count = Column(Integer, default=0)
    avg_quality_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
async def init_db():
    """Initialize the database with all tables."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise