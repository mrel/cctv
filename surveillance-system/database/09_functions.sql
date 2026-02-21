-- ============================================================
-- Utility Functions and Views
-- Helper functions for common operations
-- ============================================================

-- Function to search subjects by face embedding similarity
CREATE OR REPLACE FUNCTION search_subjects_by_face(
    query_embedding VECTOR(512),
    similarity_threshold FLOAT DEFAULT 0.7,
    max_results INTEGER DEFAULT 10
)
RETURNS TABLE (
    subject_id UUID,
    label VARCHAR(255),
    subject_type VARCHAR(50),
    similarity FLOAT,
    last_seen TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.subject_id,
        s.label,
        s.subject_type,
        1 - (s.primary_embedding <=> query_embedding) as similarity,
        s.last_seen
    FROM subjects s
    WHERE s.status = 'active'
        AND s.primary_embedding IS NOT NULL
        AND 1 - (s.primary_embedding <=> query_embedding) >= similarity_threshold
    ORDER BY s.primary_embedding <=> query_embedding
    LIMIT max_results;
END;
$$ language 'plpgsql';

-- Function to get subject timeline
CREATE OR REPLACE FUNCTION get_subject_timeline(
    p_subject_id UUID,
    p_from TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_to TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_limit INTEGER DEFAULT 100
)
RETURNS TABLE (
    sighting_id UUID,
    camera_id UUID,
    camera_name VARCHAR(255),
    image_id UUID,
    detection_confidence FLOAT,
    recognition_confidence FLOAT,
    detected_at TIMESTAMP WITH TIME ZONE,
    location VARCHAR(500)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.sighting_id,
        s.camera_id,
        c.name as camera_name,
        s.image_id,
        s.detection_confidence,
        s.recognition_confidence,
        s.detected_at,
        c.location
    FROM sightings s
    JOIN cameras c ON s.camera_id = c.camera_id
    WHERE s.subject_id = p_subject_id
        AND (p_from IS NULL OR s.detected_at >= p_from)
        AND (p_to IS NULL OR s.detected_at <= p_to)
    ORDER BY s.detected_at DESC
    LIMIT p_limit;
END;
$$ language 'plpgsql';

-- Function to get camera statistics
CREATE OR REPLACE FUNCTION get_camera_stats(
    p_camera_id UUID,
    p_from TIMESTAMP WITH TIME ZONE DEFAULT NOW() - INTERVAL '24 hours',
    p_to TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
RETURNS TABLE (
    total_detections BIGINT,
    unique_subjects BIGINT,
    avg_confidence FLOAT,
    peak_hour INTEGER,
    peak_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH hourly_counts AS (
        SELECT 
            EXTRACT(HOUR FROM detected_at)::INTEGER as hour,
            COUNT(*) as cnt
        FROM sightings
        WHERE camera_id = p_camera_id
            AND detected_at BETWEEN p_from AND p_to
        GROUP BY EXTRACT(HOUR FROM detected_at)
    ),
    stats AS (
        SELECT 
            COUNT(*) as total_detections,
            COUNT(DISTINCT subject_id) as unique_subjects,
            AVG(detection_confidence) as avg_confidence
        FROM sightings
        WHERE camera_id = p_camera_id
            AND detected_at BETWEEN p_from AND p_to
    )
    SELECT 
        s.total_detections,
        s.unique_subjects,
        s.avg_confidence,
        hc.hour as peak_hour,
        hc.cnt as peak_count
    FROM stats s
    LEFT JOIN hourly_counts hc ON hc.cnt = (SELECT MAX(cnt) FROM hourly_counts)
    LIMIT 1;
END;
$$ language 'plpgsql';

-- Function to create monthly partition for sightings
CREATE OR REPLACE FUNCTION create_sightings_partition(
    year INTEGER,
    month INTEGER
)
RETURNS TEXT AS $$
DECLARE
    partition_name TEXT;
    start_date TEXT;
    end_date TEXT;
BEGIN
    partition_name := 'sightings_y' || year || 'm' || LPAD(month::TEXT, 2, '0');
    start_date := year || '-' || LPAD(month::TEXT, 2, '0') || '-01';
    end_date := year || '-' || LPAD((month + 1)::TEXT, 2, '0') || '-01';
    
    IF month = 12 THEN
        end_date := (year + 1) || '-01-01';
    END IF;
    
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF sightings FOR VALUES FROM (%L) TO (%L)',
        partition_name, start_date, end_date
    );
    
    RETURN partition_name;
END;
$$ language 'plpgsql';

-- View for active alerts with details
CREATE VIEW active_alerts AS
SELECT 
    al.alert_id,
    al.rule_id,
    ar.name as rule_name,
    ar.rule_type,
    ar.priority as rule_priority,
    al.subject_id,
    s.label as subject_label,
    s.subject_type,
    al.camera_id,
    c.name as camera_name,
    c.location as camera_location,
    al.trigger_data,
    al.status,
    al.priority,
    al.created_at,
    al.acknowledged_by,
    al.acknowledged_at,
    EXTRACT(EPOCH FROM (NOW() - al.created_at))/60 as age_minutes
FROM alert_logs al
LEFT JOIN alert_rules ar ON al.rule_id = ar.rule_id
LEFT JOIN subjects s ON al.subject_id = s.subject_id
LEFT JOIN cameras c ON al.camera_id = c.camera_id
WHERE al.status IN ('open', 'acknowledged')
ORDER BY al.priority DESC, al.created_at DESC;

-- View for camera health status
CREATE VIEW camera_health AS
SELECT 
    c.camera_id,
    c.name,
    c.location,
    c.health_status,
    c.is_active,
    c.last_frame_at,
    CASE 
        WHEN c.last_frame_at IS NULL THEN 'never'
        WHEN c.last_frame_at < NOW() - INTERVAL '5 minutes' THEN 'stale'
        ELSE 'fresh'
    END as frame_freshness,
    COUNT(s.sighting_id) FILTER (WHERE s.detected_at > NOW() - INTERVAL '1 hour') as detections_last_hour,
    MAX(s.detected_at) as last_detection_at
FROM cameras c
LEFT JOIN sightings s ON c.camera_id = s.camera_id
GROUP BY c.camera_id, c.name, c.location, c.health_status, c.is_active, c.last_frame_at;

-- View for GDPR data export (all data about a subject)
CREATE VIEW subject_gdpr_export AS
SELECT 
    s.subject_id,
    s.label,
    s.subject_type,
    s.status,
    s.enrollment_date,
    s.last_seen,
    s.metadata,
    s.consent_status,
    s.retention_until,
    json_agg(DISTINCT jsonb_build_object(
        'image_id', i.image_id,
        'image_type', i.image_type,
        'storage_path', i.storage_path,
        'captured_at', i.captured_at,
        'camera_id', i.camera_id
    )) as images,
    json_agg(DISTINCT jsonb_build_object(
        'sighting_id', si.sighting_id,
        'camera_id', si.camera_id,
        'detected_at', si.detected_at,
        'detection_confidence', si.detection_confidence,
        'recognition_confidence', si.recognition_confidence
    )) as sightings,
    json_agg(DISTINCT jsonb_build_object(
        'alert_id', al.alert_id,
        'rule_type', ar.rule_type,
        'created_at', al.created_at,
        'status', al.status
    )) as alerts
FROM subjects s
LEFT JOIN images i ON s.subject_id = i.subject_id
LEFT JOIN sightings si ON s.subject_id = si.subject_id
LEFT JOIN alert_logs al ON s.subject_id = al.subject_id
LEFT JOIN alert_rules ar ON al.rule_id = ar.rule_id
GROUP BY s.subject_id, s.label, s.subject_type, s.status, s.enrollment_date, 
         s.last_seen, s.metadata, s.consent_status, s.retention_until;

-- Comments
COMMENT ON FUNCTION search_subjects_by_face IS 'Vector similarity search for face recognition';
COMMENT ON FUNCTION get_subject_timeline IS 'Get chronological movement history for a subject';
COMMENT ON FUNCTION get_camera_stats IS 'Get detection statistics for a camera';
COMMENT ON FUNCTION create_sightings_partition IS 'Create monthly partition for sightings table';
