-- ============================================================
-- Audit & Compliance Table (Immutable)
-- GDPR-compliant audit trail for all data access
-- ============================================================

CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    user_role VARCHAR(50),
    action VARCHAR(100) NOT NULL, -- 'view_subject', 'export_data', 'delete_image'
    resource_type VARCHAR(50), -- 'subject', 'image', 'camera', 'alert', 'setting'
    resource_id UUID,
    details JSONB, -- Additional context about the action
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    compliance_context JSONB, -- GDPR lawful basis, retention justification
    
    -- Constraints
    CONSTRAINT valid_action CHECK (action IN (
        'login', 'logout', 'view_subject', 'view_image', 'view_camera', 
        'create_subject', 'update_subject', 'delete_subject',
        'create_camera', 'update_camera', 'delete_camera',
        'create_rule', 'update_rule', 'delete_rule',
        'export_data', 'import_data', 'search_by_image',
        'acknowledge_alert', 'resolve_alert', 'settings_change',
        'gdpr_export', 'gdpr_delete', 'consent_update'
    )),
    CONSTRAINT valid_resource_type CHECK (resource_type IN ('subject', 'image', 'camera', 'alert', 'rule', 'setting', 'user', 'system'))
);

-- Indexes for audit_logs
CREATE INDEX idx_audit_user_time ON audit_logs(user_id, timestamp DESC);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_ip ON audit_logs(ip_address);
CREATE INDEX idx_audit_compliance ON audit_logs USING gin(compliance_context);

-- Partial indexes for common compliance queries
CREATE INDEX idx_audit_gdpr_actions ON audit_logs(user_id, timestamp DESC)
    WHERE action IN ('gdpr_export', 'gdpr_delete', 'view_subject', 'export_data');

CREATE INDEX idx_audit_subject_access ON audit_logs(resource_id, timestamp DESC)
    WHERE resource_type = 'subject' AND action IN ('view_subject', 'export_data', 'search_by_image');

-- Function to prevent audit log updates (immutable)
CREATE OR REPLACE FUNCTION prevent_audit_update()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit logs are immutable and cannot be modified';
END;
$$ language 'plpgsql';

CREATE TRIGGER audit_logs_immutable
    BEFORE UPDATE OR DELETE ON audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_update();

-- Function for automated audit logging
CREATE OR REPLACE FUNCTION log_audit_event(
    p_user_id UUID,
    p_user_role VARCHAR(50),
    p_action VARCHAR(100),
    p_resource_type VARCHAR(50),
    p_resource_id UUID,
    p_details JSONB DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_compliance_context JSONB DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO audit_logs (
        user_id, user_role, action, resource_type, resource_id,
        details, ip_address, user_agent, compliance_context
    ) VALUES (
        p_user_id, p_user_role, p_action, p_resource_type, p_resource_id,
        p_details, p_ip_address, p_user_agent, p_compliance_context
    )
    RETURNING log_id INTO v_log_id;
    
    RETURN v_log_id;
END;
$$ language 'plpgsql';

-- View for GDPR compliance reports
CREATE VIEW gdpr_audit_summary AS
SELECT 
    user_id,
    action,
    resource_type,
    COUNT(*) as action_count,
    MIN(timestamp) as first_access,
    MAX(timestamp) as last_access
FROM audit_logs
WHERE action IN ('view_subject', 'export_data', 'gdpr_export', 'gdpr_delete', 'search_by_image')
GROUP BY user_id, action, resource_type;

-- Comments
COMMENT ON TABLE audit_logs IS 'Immutable audit trail for GDPR compliance and security monitoring';
COMMENT ON COLUMN audit_logs.action IS 'Type of action performed by user';
COMMENT ON COLUMN audit_logs.compliance_context IS 'GDPR lawful basis and retention justification';
COMMENT ON COLUMN audit_logs.details IS 'Additional context: search queries, filter parameters';
