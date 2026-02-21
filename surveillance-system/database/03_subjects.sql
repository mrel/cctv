-- ============================================================
-- Subject Identity Management Table
-- Stores known and unknown person identities with face embeddings
-- ============================================================

CREATE TABLE subjects (
    subject_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    label VARCHAR(255), -- "John Doe" or "Unknown-4521"
    subject_type VARCHAR(50) DEFAULT 'unknown', -- 'employee', 'visitor', 'banned', 'vip'
    status VARCHAR(50) DEFAULT 'active',
    primary_embedding VECTOR(512), -- ArcFace embedding vector
    enrollment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE,
    metadata JSONB, -- estimated_age, gender, ethnicity, clothing_preferences
    consent_status VARCHAR(50) DEFAULT 'pending', -- GDPR compliance
    retention_until TIMESTAMP WITH TIME ZONE, -- Auto-deletion date
    
    -- Constraints
    CONSTRAINT valid_subject_type CHECK (subject_type IN ('employee', 'visitor', 'banned', 'vip', 'unknown')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'inactive', 'archived')),
    CONSTRAINT valid_consent CHECK (consent_status IN ('granted', 'denied', 'pending', 'withdrawn'))
);

-- Indexes for subjects
CREATE INDEX idx_subjects_type ON subjects(subject_type);
CREATE INDEX idx_subjects_status ON subjects(status);
CREATE INDEX idx_subjects_label ON subjects USING gin(label gin_trgm_ops);
CREATE INDEX idx_subjects_last_seen ON subjects(last_seen DESC);
CREATE INDEX idx_subjects_consent ON subjects(consent_status);

-- Vector similarity search index using ivfflat
CREATE INDEX idx_subjects_embedding ON subjects 
    USING ivfflat (primary_embedding vector_cosine_ops)
    WITH (lists = 100);

-- Partial index for active subjects only (common query pattern)
CREATE INDEX idx_subjects_active_embedding ON subjects 
    USING ivfflat (primary_embedding vector_cosine_ops)
    WHERE status = 'active';

-- Trigger for retention policy
CREATE OR REPLACE FUNCTION check_retention_policy()
RETURNS TRIGGER AS $$
BEGIN
    -- Auto-delete subjects past retention date
    IF NEW.retention_until IS NOT NULL AND NEW.retention_until < NOW() THEN
        RAISE NOTICE 'Subject % has exceeded retention period', NEW.subject_id;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER enforce_retention_policy
    BEFORE INSERT OR UPDATE ON subjects
    FOR EACH ROW
    EXECUTE FUNCTION check_retention_policy();

-- Comments
COMMENT ON TABLE subjects IS 'Person identities with facial recognition embeddings';
COMMENT ON COLUMN subjects.primary_embedding IS '512-dimensional ArcFace embedding vector for face recognition';
COMMENT ON COLUMN subjects.metadata IS 'Additional attributes: age, gender, ethnicity, clothing preferences';
COMMENT ON COLUMN subjects.consent_status IS 'GDPR consent status for data processing';
COMMENT ON COLUMN subjects.retention_until IS 'Automatic deletion date for GDPR compliance';
