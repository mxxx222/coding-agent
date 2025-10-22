-- Enhanced cost tracking and analytics
-- This migration adds advanced cost tracking and user analytics

-- Add cost tracking enhancements
ALTER TABLE cost_tracking ADD COLUMN IF NOT EXISTS model_used VARCHAR(100);
ALTER TABLE cost_tracking ADD COLUMN IF NOT EXISTS prompt_tokens INTEGER;
ALTER TABLE cost_tracking ADD COLUMN IF NOT EXISTS completion_tokens INTEGER;
ALTER TABLE cost_tracking ADD COLUMN IF NOT EXISTS total_tokens INTEGER;

-- Add user analytics table
CREATE TABLE user_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    requests_count INTEGER DEFAULT 0,
    total_cost DECIMAL(10,4) DEFAULT 0,
    avg_response_time_ms INTEGER,
    most_used_endpoint VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Add project analytics table
CREATE TABLE project_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    analysis_count INTEGER DEFAULT 0,
    refactor_suggestions_count INTEGER DEFAULT 0,
    test_generations_count INTEGER DEFAULT 0,
    avg_quality_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, date)
);

-- Add indexes for analytics
CREATE INDEX idx_user_analytics_user_id ON user_analytics(user_id);
CREATE INDEX idx_user_analytics_date ON user_analytics(date);
CREATE INDEX idx_project_analytics_project_id ON project_analytics(project_id);
CREATE INDEX idx_project_analytics_date ON project_analytics(date);

-- Create views for analytics
CREATE VIEW daily_user_stats AS
SELECT 
    u.id as user_id,
    u.email,
    u.name,
    ua.date,
    ua.requests_count,
    ua.total_cost,
    ua.avg_response_time_ms,
    ua.most_used_endpoint
FROM users u
JOIN user_analytics ua ON u.id = ua.user_id
ORDER BY ua.date DESC;

CREATE VIEW daily_project_stats AS
SELECT 
    p.id as project_id,
    p.name as project_name,
    p.language,
    p.framework,
    pa.date,
    pa.analysis_count,
    pa.refactor_suggestions_count,
    pa.test_generations_count,
    pa.avg_quality_score
FROM projects p
JOIN project_analytics pa ON p.id = pa.project_id
ORDER BY pa.date DESC;

-- Create function to update daily analytics
CREATE OR REPLACE FUNCTION update_daily_analytics()
RETURNS TRIGGER AS $$
BEGIN
    -- Update user analytics
    INSERT INTO user_analytics (user_id, date, requests_count, total_cost, avg_response_time_ms, most_used_endpoint)
    VALUES (
        NEW.user_id,
        CURRENT_DATE,
        1,
        NEW.cost_amount,
        NEW.response_time_ms,
        NEW.endpoint
    )
    ON CONFLICT (user_id, date) DO UPDATE SET
        requests_count = user_analytics.requests_count + 1,
        total_cost = user_analytics.total_cost + NEW.cost_amount,
        avg_response_time_ms = (user_analytics.avg_response_time_ms + NEW.response_time_ms) / 2,
        most_used_endpoint = CASE 
            WHEN user_analytics.requests_count = 0 THEN NEW.endpoint
            ELSE user_analytics.most_used_endpoint
        END;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic analytics updates
CREATE TRIGGER update_analytics_on_cost_tracking
    AFTER INSERT ON cost_tracking
    FOR EACH ROW EXECUTE FUNCTION update_daily_analytics();

-- Add cost limits and quotas
ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_cost_limit DECIMAL(10,2) DEFAULT 10.00;
ALTER TABLE users ADD COLUMN IF NOT EXISTS monthly_cost_limit DECIMAL(10,2) DEFAULT 100.00;
ALTER TABLE users ADD COLUMN IF NOT EXISTS request_rate_limit INTEGER DEFAULT 100;

-- Create cost limit check function
CREATE OR REPLACE FUNCTION check_cost_limits(p_user_id UUID, p_cost_amount DECIMAL)
RETURNS BOOLEAN AS $$
DECLARE
    daily_cost DECIMAL;
    monthly_cost DECIMAL;
    daily_limit DECIMAL;
    monthly_limit DECIMAL;
BEGIN
    -- Get user limits
    SELECT daily_cost_limit, monthly_cost_limit 
    INTO daily_limit, monthly_limit
    FROM users WHERE id = p_user_id;
    
    -- Check daily cost
    SELECT COALESCE(SUM(cost_amount), 0)
    INTO daily_cost
    FROM cost_tracking 
    WHERE user_id = p_user_id 
    AND created_at >= CURRENT_DATE;
    
    -- Check monthly cost
    SELECT COALESCE(SUM(cost_amount), 0)
    INTO monthly_cost
    FROM cost_tracking 
    WHERE user_id = p_user_id 
    AND created_at >= DATE_TRUNC('month', CURRENT_DATE);
    
    -- Check if adding this cost would exceed limits
    IF (daily_cost + p_cost_amount) > daily_limit THEN
        RETURN FALSE;
    END IF;
    
    IF (monthly_cost + p_cost_amount) > monthly_limit THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
