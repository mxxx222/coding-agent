-- Coding Agent Database Schema
-- This file contains the complete database schema for the Coding Agent system

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    cost_limit DECIMAL(10,2) DEFAULT 100.00,
    is_active BOOLEAN DEFAULT TRUE
);

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    language VARCHAR(50),
    framework VARCHAR(100),
    repository_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Code analysis results
CREATE TABLE code_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    code_hash VARCHAR(64) NOT NULL,
    language VARCHAR(50),
    complexity_score INTEGER,
    quality_score DECIMAL(3,2),
    line_count INTEGER,
    function_count INTEGER,
    class_count INTEGER,
    analysis_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Refactoring suggestions
CREATE TABLE refactor_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code_analysis_id UUID REFERENCES code_analyses(id) ON DELETE CASCADE,
    suggestion_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    current_code TEXT,
    suggested_code TEXT,
    reasoning TEXT,
    line_number INTEGER,
    confidence_score DECIMAL(3,2),
    status VARCHAR(20) DEFAULT 'pending', -- pending, applied, rejected
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_at TIMESTAMP WITH TIME ZONE
);

-- Test generations
CREATE TABLE test_generations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code_analysis_id UUID REFERENCES code_analyses(id) ON DELETE CASCADE,
    test_framework VARCHAR(50) NOT NULL,
    test_type VARCHAR(20) NOT NULL, -- unit, integration, e2e
    test_code TEXT NOT NULL,
    test_file_path VARCHAR(500),
    coverage_estimate DECIMAL(3,2),
    test_count INTEGER,
    status VARCHAR(20) DEFAULT 'generated', -- generated, running, passed, failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed_at TIMESTAMP WITH TIME ZONE
);

-- Integrations
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    service_name VARCHAR(100) NOT NULL,
    service_type VARCHAR(50) NOT NULL, -- database, payment, auth, deployment
    config_data JSONB NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cost tracking
CREATE TABLE cost_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    operation_type VARCHAR(50) NOT NULL, -- analyze, refactor, test, generate
    tokens_used INTEGER,
    cost_amount DECIMAL(10,4) NOT NULL,
    endpoint VARCHAR(100),
    request_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vector embeddings for code similarity
CREATE TABLE code_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code_analysis_id UUID REFERENCES code_analyses(id) ON DELETE CASCADE,
    embedding_vector REAL[] NOT NULL,
    embedding_model VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API usage logs
CREATE TABLE api_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_api_key ON users(api_key);
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_code_analyses_project_id ON code_analyses(project_id);
CREATE INDEX idx_code_analyses_created_at ON code_analyses(created_at);
CREATE INDEX idx_refactor_suggestions_code_analysis_id ON refactor_suggestions(code_analysis_id);
CREATE INDEX idx_refactor_suggestions_status ON refactor_suggestions(status);
CREATE INDEX idx_test_generations_code_analysis_id ON test_generations(code_analysis_id);
CREATE INDEX idx_integrations_user_id ON integrations(user_id);
CREATE INDEX idx_integrations_service_name ON integrations(service_name);
CREATE INDEX idx_cost_tracking_user_id ON cost_tracking(user_id);
CREATE INDEX idx_cost_tracking_created_at ON cost_tracking(created_at);
CREATE INDEX idx_api_logs_user_id ON api_logs(user_id);
CREATE INDEX idx_api_logs_created_at ON api_logs(created_at);

-- Full-text search indexes
CREATE INDEX idx_code_analyses_analysis_data_gin ON code_analyses USING GIN (analysis_data);
CREATE INDEX idx_refactor_suggestions_description_gin ON refactor_suggestions USING GIN (to_tsvector('english', description));
CREATE INDEX idx_integrations_config_data_gin ON integrations USING GIN (config_data);

-- Functions for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE VIEW user_cost_summary AS
SELECT 
    u.id as user_id,
    u.email,
    u.name,
    COALESCE(SUM(ct.cost_amount), 0) as total_cost,
    COUNT(ct.id) as total_requests,
    MAX(ct.created_at) as last_request
FROM users u
LEFT JOIN cost_tracking ct ON u.id = ct.user_id
GROUP BY u.id, u.email, u.name;

CREATE VIEW project_analytics AS
SELECT 
    p.id as project_id,
    p.name as project_name,
    p.language,
    p.framework,
    COUNT(ca.id) as analysis_count,
    AVG(ca.quality_score) as avg_quality_score,
    AVG(ca.complexity_score) as avg_complexity,
    COUNT(rs.id) as suggestion_count,
    COUNT(tg.id) as test_count
FROM projects p
LEFT JOIN code_analyses ca ON p.id = ca.project_id
LEFT JOIN refactor_suggestions rs ON ca.id = rs.code_analysis_id
LEFT JOIN test_generations tg ON ca.id = tg.code_analysis_id
GROUP BY p.id, p.name, p.language, p.framework;

-- Row Level Security (RLS) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE code_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE refactor_suggestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE code_embeddings ENABLE ROW LEVEL SECURITY;

-- RLS Policies (users can only access their own data)
CREATE POLICY user_isolation ON users FOR ALL TO authenticated USING (id = current_setting('app.current_user_id')::uuid);
CREATE POLICY project_isolation ON projects FOR ALL TO authenticated USING (user_id = current_setting('app.current_user_id')::uuid);
CREATE POLICY code_analysis_isolation ON code_analyses FOR ALL TO authenticated USING (project_id IN (SELECT id FROM projects WHERE user_id = current_setting('app.current_user_id')::uuid));
CREATE POLICY refactor_suggestion_isolation ON refactor_suggestions FOR ALL TO authenticated USING (code_analysis_id IN (SELECT id FROM code_analyses WHERE project_id IN (SELECT id FROM projects WHERE user_id = current_setting('app.current_user_id')::uuid)));
CREATE POLICY test_generation_isolation ON test_generations FOR ALL TO authenticated USING (code_analysis_id IN (SELECT id FROM code_analyses WHERE project_id IN (SELECT id FROM projects WHERE user_id = current_setting('app.current_user_id')::uuid)));
CREATE POLICY integration_isolation ON integrations FOR ALL TO authenticated USING (user_id = current_setting('app.current_user_id')::uuid);
CREATE POLICY cost_tracking_isolation ON cost_tracking FOR ALL TO authenticated USING (user_id = current_setting('app.current_user_id')::uuid);
CREATE POLICY code_embedding_isolation ON code_embeddings FOR ALL TO authenticated USING (code_analysis_id IN (SELECT id FROM code_analyses WHERE project_id IN (SELECT id FROM projects WHERE user_id = current_setting('app.current_user_id')::uuid)));