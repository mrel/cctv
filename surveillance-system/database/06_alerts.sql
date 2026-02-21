-- ============================================================
-- Alert Rules & Alert Logs Tables
-- Rule engine for automated security notifications
-- ============================================================

-- Alert Rules Table
CREATE TABLE alert_rules (
    rule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    rule_type VARCHAR(50) NOT NULL, -- 'blacklist', 'geofence', 'loitering', 'tailgating'
    conditions JSONB NOT NULL, -- Complex rule definition
    actions JSONB, -- webhook, email, sms, push_notification
    is_active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10), -- 1-10 scale
    cooldown_seconds INTEGER DEFAULT 300, -- Minimum time between repeat alerts
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_rule_type CHECK (rule_type IN ('blacklist', 'whitelist', 'geofence', 'loitering', 'tailgating', 'crowd', 'time_restriction', 'custom')),
    CONSTRAINT valid_priority CHECK (priority >= 1 AND priority <= 10)
);

-- Alert Logs Table
CREATE TABLE alert_logs (
    alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_id UUID REFERENCES alert_rules(rule_id) ON DELETE SET NULL,
    subject_id UUID REFERENCES subjects(subject_id) ON DELETE SET NULL,
    camera_id UUID REFERENCES cameras(camera_id) ON DELETE SET NULL,
    sighting_id UUID REFERENCES sightings(sighting_id) ON DELETE SET NULL,
    trigger_data JSONB NOT NULL, -- Snapshot of triggering event
    status VARCHAR(50) DEFAULT 'open', -- open, acknowledged, resolved, false_positive
    priority INTEGER,
    acknowledged_by UUID,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_alert_status CHECK (status IN ('open', 'acknowledged', 'resolved', 'false_positive', 'escalated'))
);

-- Indexes for alert_rules
CREATE INDEX idx_alert_rules_active ON alert_rules(is_active);
CREATE INDEX idx_alert_rules_type ON alert_rules(rule_type);
CREATE INDEX idx_alert_rules_priority ON alert_rules(priority);

-- Indexes for alert_logs
CREATE INDEX idx_alert_logs_status ON alert_logs(status);
CREATE INDEX idx_alert_logs_rule ON alert_logs(rule_id);
CREATE INDEX idx_alert_logs_subject ON alert_logs(subject_id);
CREATE INDEX idx_alert_logs_camera ON alert_logs(camera_id);
CREATE INDEX idx_alert_logs_created ON alert_logs(created_at DESC);
CREATE INDEX idx_alert_logs_status_created ON alert_logs(status, created_at DESC);

-- Partial index for open alerts (common query pattern)
CREATE INDEX idx_alert_logs_open ON alert_logs(created_at DESC)
    WHERE status = 'open';

-- Trigger to update updated_at on alert_rules
CREATE TRIGGER update_alert_rules_updated_at
    BEFORE UPDATE ON alert_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to auto-set priority from rule
CREATE OR REPLACE FUNCTION set_alert_priority()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.priority IS NULL AND NEW.rule_id IS NOT NULL THEN
        SELECT priority INTO NEW.priority 
        FROM alert_rules 
        WHERE rule_id = NEW.rule_id;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER auto_set_alert_priority
    BEFORE INSERT ON alert_logs
    FOR EACH ROW
    EXECUTE FUNCTION set_alert_priority();

-- Comments
COMMENT ON TABLE alert_rules IS 'Configuration for automated alert rules and triggers';
COMMENT ON COLUMN alert_rules.conditions IS 'JSON rule definition: subject filters, camera zones, time windows';
COMMENT ON COLUMN alert_rules.actions IS 'Notification actions: webhook URLs, email addresses, SMS numbers';
COMMENT ON COLUMN alert_rules.cooldown_seconds IS 'Minimum seconds before same rule can trigger again';
COMMENT ON TABLE alert_logs IS 'Log of all triggered alerts with status tracking';
COMMENT ON COLUMN alert_logs.trigger_data IS 'Snapshot of event data that triggered the alert';
