-- Add embeddings support
-- This migration adds vector embeddings for code similarity search

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

-- Add indexes for embeddings
CREATE INDEX idx_code_embeddings_code_analysis_id ON code_embeddings(code_analysis_id);
CREATE INDEX idx_code_embeddings_model ON code_embeddings(embedding_model);

-- Add indexes for API logs
CREATE INDEX idx_api_logs_user_id ON api_logs(user_id);
CREATE INDEX idx_api_logs_created_at ON api_logs(created_at);
CREATE INDEX idx_api_logs_endpoint ON api_logs(endpoint);

-- Add GIN indexes for JSONB columns
CREATE INDEX idx_code_analyses_analysis_data_gin ON code_analyses USING GIN (analysis_data);
CREATE INDEX idx_integrations_config_data_gin ON integrations USING GIN (config_data);

-- Add full-text search index for refactor suggestions
CREATE INDEX idx_refactor_suggestions_description_gin ON refactor_suggestions USING GIN (to_tsvector('english', description));
