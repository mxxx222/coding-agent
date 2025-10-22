-- Initial database migration
-- Creates the core tables for the Coding Agent system

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
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_at TIMESTAMP WITH TIME ZONE
);

-- Test generations
CREATE TABLE test_generations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code_analysis_id UUID REFERENCES code_analyses(id) ON DELETE CASCADE,
    test_framework VARCHAR(50) NOT NULL,
    test_type VARCHAR(20) NOT NULL,
    test_code TEXT NOT NULL,
    test_file_path VARCHAR(500),
    coverage_estimate DECIMAL(3,2),
    test_count INTEGER,
    status VARCHAR(20) DEFAULT 'generated',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed_at TIMESTAMP WITH TIME ZONE
);

-- Integrations
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    service_name VARCHAR(100) NOT NULL,
    service_type VARCHAR(50) NOT NULL,
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
    operation_type VARCHAR(50) NOT NULL,
    tokens_used INTEGER,
    cost_amount DECIMAL(10,4) NOT NULL,
    endpoint VARCHAR(100),
    request_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_api_key ON users(api_key);
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_code_analyses_project_id ON code_analyses(project_id);
CREATE INDEX idx_refactor_suggestions_code_analysis_id ON refactor_suggestions(code_analysis_id);
CREATE INDEX idx_test_generations_code_analysis_id ON test_generations(code_analysis_id);
CREATE INDEX idx_integrations_user_id ON integrations(user_id);
CREATE INDEX idx_cost_tracking_user_id ON cost_tracking(user_id);

-- Create update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
