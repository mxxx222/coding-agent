-- Add work items and relationships support
-- This migration adds graph-like relationships for work items

-- Work items table
CREATE TABLE work_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL, -- task, bug, feature, epic, story, issue, pr, commit, test, deployment
    status VARCHAR(50) NOT NULL DEFAULT 'open', -- open, in_progress, blocked, closed, cancelled
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,
    reporter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES work_items(id) ON DELETE CASCADE, -- for hierarchical relationships
    estimated_hours DECIMAL(6,2),
    actual_hours DECIMAL(6,2),
    due_date TIMESTAMP WITH TIME ZONE,
    tags TEXT[], -- array of tags
    metadata JSONB, -- flexible metadata storage
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE
);

-- Work item relationships table (for graph relationships)
CREATE TABLE work_item_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_item_id UUID NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
    target_item_id UUID NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL, -- depends_on, blocks, relates_to, duplicates, parent_of, child_of
    description TEXT,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- Prevent self-references and duplicate relationships
    CONSTRAINT no_self_reference CHECK (source_item_id != target_item_id),
    CONSTRAINT unique_relationship UNIQUE (source_item_id, target_item_id, relationship_type)
);

-- Work item comments
CREATE TABLE work_item_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    work_item_id UUID NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT FALSE, -- internal comments not visible to all users
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Work item attachments
CREATE TABLE work_item_attachments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    work_item_id UUID NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Work item history/changelog
CREATE TABLE work_item_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    work_item_id UUID NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
    changed_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    change_type VARCHAR(20) DEFAULT 'update', -- create, update, delete
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_work_items_project_id ON work_items(project_id);
CREATE INDEX idx_work_items_assignee_id ON work_items(assignee_id);
CREATE INDEX idx_work_items_reporter_id ON work_items(reporter_id);
CREATE INDEX idx_work_items_parent_id ON work_items(parent_id);
CREATE INDEX idx_work_items_status ON work_items(status);
CREATE INDEX idx_work_items_type ON work_items(type);
CREATE INDEX idx_work_items_priority ON work_items(priority);
CREATE INDEX idx_work_items_due_date ON work_items(due_date);
CREATE INDEX idx_work_items_created_at ON work_items(created_at);
CREATE INDEX idx_work_items_tags ON work_items USING GIN (tags);
CREATE INDEX idx_work_items_metadata ON work_items USING GIN (metadata);

CREATE INDEX idx_work_item_relationships_source ON work_item_relationships(source_item_id);
CREATE INDEX idx_work_item_relationships_target ON work_item_relationships(target_item_id);
CREATE INDEX idx_work_item_relationships_type ON work_item_relationships(relationship_type);
CREATE INDEX idx_work_item_relationships_created_at ON work_item_relationships(created_at);

CREATE INDEX idx_work_item_comments_item_id ON work_item_comments(work_item_id);
CREATE INDEX idx_work_item_comments_author_id ON work_item_comments(author_id);
CREATE INDEX idx_work_item_comments_created_at ON work_item_comments(created_at);

CREATE INDEX idx_work_item_attachments_item_id ON work_item_attachments(work_item_id);
CREATE INDEX idx_work_item_attachments_uploaded_by ON work_item_attachments(uploaded_by);

CREATE INDEX idx_work_item_history_item_id ON work_item_history(work_item_id);
CREATE INDEX idx_work_item_history_changed_by ON work_item_history(changed_by);
CREATE INDEX idx_work_item_history_created_at ON work_item_history(created_at);

-- Full-text search indexes
CREATE INDEX idx_work_items_title_description_gin ON work_items USING GIN (to_tsvector('english', title || ' ' || COALESCE(description, '')));
CREATE INDEX idx_work_item_comments_content_gin ON work_item_comments USING GIN (to_tsvector('english', content));

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_work_items_updated_at BEFORE UPDATE ON work_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_work_item_relationships_updated_at BEFORE UPDATE ON work_item_relationships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_work_item_comments_updated_at BEFORE UPDATE ON work_item_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically close work items when status changes to closed
CREATE OR REPLACE FUNCTION set_work_item_closed_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status IN ('closed', 'cancelled') AND OLD.status NOT IN ('closed', 'cancelled') THEN
        NEW.closed_at = NOW();
    ELSIF NEW.status NOT IN ('closed', 'cancelled') AND OLD.status IN ('closed', 'cancelled') THEN
        NEW.closed_at = NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_work_item_closed_at BEFORE UPDATE ON work_items
    FOR EACH ROW EXECUTE FUNCTION set_work_item_closed_at();

-- Function to log work item changes to history
CREATE OR REPLACE FUNCTION log_work_item_changes()
RETURNS TRIGGER AS $$
DECLARE
    change_record RECORD;
    old_json JSONB;
    new_json JSONB;
    field_name TEXT;
    old_val TEXT;
    new_val TEXT;
BEGIN
    -- Only log if this is an update
    IF TG_OP = 'UPDATE' THEN
        -- Convert rows to JSONB for comparison
        old_json := to_jsonb(OLD);
        new_json := to_jsonb(NEW);

        -- Log changes for each field
        FOR field_name IN SELECT jsonb_object_keys(new_json)
        LOOP
            IF old_json->field_name IS DISTINCT FROM new_json->field_name THEN
                -- Get string representations
                old_val := old_json->>field_name;
                new_val := new_json->>field_name;

                -- Insert history record
                INSERT INTO work_item_history (
                    work_item_id,
                    changed_by,
                    field_name,
                    old_value,
                    new_value,
                    change_type
                ) VALUES (
                    NEW.id,
                    NEW.updated_by, -- Assuming we add updated_by field, or use current user
                    field_name,
                    old_val,
                    new_val,
                    'update'
                );
            END IF;
        END LOOP;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Note: The history trigger would need updated_by field added to work_items table
-- For now, we'll skip the automatic history logging to keep the schema simpler

-- Row Level Security (RLS) policies
ALTER TABLE work_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE work_item_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE work_item_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE work_item_attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE work_item_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies (users can only access work items from projects they have access to)
CREATE POLICY work_items_isolation ON work_items FOR ALL TO authenticated USING (
    project_id IN (
        SELECT id FROM projects WHERE user_id = current_setting('app.current_user_id')::uuid
    )
);

CREATE POLICY work_item_relationships_isolation ON work_item_relationships FOR ALL TO authenticated USING (
    source_item_id IN (
        SELECT wi.id FROM work_items wi
        JOIN projects p ON wi.project_id = p.id
        WHERE p.user_id = current_setting('app.current_user_id')::uuid
    )
);

CREATE POLICY work_item_comments_isolation ON work_item_comments FOR ALL TO authenticated USING (
    work_item_id IN (
        SELECT wi.id FROM work_items wi
        JOIN projects p ON wi.project_id = p.id
        WHERE p.user_id = current_setting('app.current_user_id')::uuid
    )
);

CREATE POLICY work_item_attachments_isolation ON work_item_attachments FOR ALL TO authenticated USING (
    work_item_id IN (
        SELECT wi.id FROM work_items wi
        JOIN projects p ON wi.project_id = p.id
        WHERE p.user_id = current_setting('app.current_user_id')::uuid
    )
);

CREATE POLICY work_item_history_isolation ON work_item_history FOR ALL TO authenticated USING (
    work_item_id IN (
        SELECT wi.id FROM work_items wi
        JOIN projects p ON wi.project_id = p.id
        WHERE p.user_id = current_setting('app.current_user_id')::uuid
    )
);