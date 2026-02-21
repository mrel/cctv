-- ============================================================
-- Seed Data for Development and Testing
-- Sample cameras, subjects, and test data
-- ============================================================

-- Insert sample cameras
INSERT INTO cameras (camera_id, name, location, rtsp_url, stream_config, detection_zones, is_active, health_status) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'Main Entrance', 'Building A - Floor 1', 'rtsp://admin:pass@192.168.1.10:554/stream1', 
    '{"protocol": "rtsp", "resolution": "1920x1080", "fps": 15, "codec": "h264", "auth_type": "basic"}'::jsonb,
    '[{"x": 0.1, "y": 0.1, "w": 0.8, "h": 0.8}]'::jsonb, true, 'healthy'),
('550e8400-e29b-41d4-a716-446655440001', 'Lobby North', 'Building A - Floor 1', 'rtsp://admin:pass@192.168.1.11:554/stream1',
    '{"protocol": "rtsp", "resolution": "1920x1080", "fps": 15, "codec": "h264", "auth_type": "basic"}'::jsonb,
    '[{"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0}]'::jsonb, true, 'healthy'),
('550e8400-e29b-41d4-a716-446655440002', 'Parking Garage', 'Building A - Basement', 'rtsp://admin:pass@192.168.1.12:554/stream1',
    '{"protocol": "rtsp", "resolution": "1280x720", "fps": 10, "codec": "h264", "auth_type": "digest"}'::jsonb,
    '[{"x": 0.2, "y": 0.3, "w": 0.6, "h": 0.5}]'::jsonb, true, 'degraded'),
('550e8400-e29b-41d4-a716-446655440003', 'Server Room', 'Building A - Floor 2', 'rtsp://admin:pass@192.168.1.13:554/stream1',
    '{"protocol": "rtsp", "resolution": "1920x1080", "fps": 30, "codec": "h265", "auth_type": "basic"}'::jsonb,
    '[{"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0}]'::jsonb, true, 'healthy'),
('550e8400-e29b-41d4-a716-446655440004', 'Loading Dock', 'Building A - Rear', 'rtsp://admin:pass@192.168.1.14:554/stream1',
    '{"protocol": "rtsp", "resolution": "2560x1440", "fps": 20, "codec": "h264", "auth_type": "basic"}'::jsonb,
    '[{"x": 0.1, "y": 0.2, "w": 0.7, "h": 0.6}]'::jsonb, false, 'disconnected');

-- Insert sample subjects with random embeddings
INSERT INTO subjects (subject_id, label, subject_type, status, metadata, consent_status) VALUES
('660e8400-e29b-41d4-a716-446655440000', 'John Smith', 'employee', 'active', 
    '{"estimated_age": 35, "gender": "male", "department": "Engineering"}'::jsonb, 'granted'),
('660e8400-e29b-41d4-a716-446655440001', 'Sarah Johnson', 'employee', 'active',
    '{"estimated_age": 28, "gender": "female", "department": "Marketing"}'::jsonb, 'granted'),
('660e8400-e29b-41d4-a716-446655440002', 'Michael Chen', 'employee', 'active',
    '{"estimated_age": 42, "gender": "male", "department": "Security"}'::jsonb, 'granted'),
('660e8400-e29b-41d4-a716-446655440003', 'Emily Davis', 'visitor', 'active',
    '{"estimated_age": 31, "gender": "female", "visit_reason": "interview"}'::jsonb, 'pending'),
('660e8400-e29b-41d4-a716-446655440004', 'Unknown-0001', 'unknown', 'active',
    '{"estimated_age": 25, "gender": "male"}'::jsonb, 'pending'),
('660e8400-e29b-41d4-a716-446655440005', 'Robert Wilson', 'banned', 'active',
    '{"estimated_age": 45, "gender": "male", "ban_reason": "trespassing"}'::jsonb, 'denied'),
('660e8400-e29b-41d4-a716-446655440006', 'VIP Guest', 'vip', 'active',
    '{"estimated_age": 50, "gender": "female", "vip_level": "platinum"}'::jsonb, 'granted');

-- Insert sample alert rules
INSERT INTO alert_rules (rule_id, name, description, rule_type, conditions, actions, priority, is_active) VALUES
('770e8400-e29b-41d4-a716-446655440000', 'Banned Person Detected', 'Alert when banned subject is detected', 'blacklist',
    '{"subject_types": ["banned"], "cameras": ["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"], "min_confidence": 0.8}'::jsonb,
    '{"webhook": "https://security.company.com/alerts", "email": ["security@company.com"], "push": true}'::jsonb,
    10, true),
('770e8400-e29b-41d4-a716-446655440001', 'VIP Arrival', 'Notify when VIP enters main entrance', 'whitelist',
    '{"subject_types": ["vip"], "cameras": ["550e8400-e29b-41d4-a716-446655440000"], "min_confidence": 0.85}'::jsonb,
    '{"email": ["reception@company.com"], "push": true}'::jsonb,
    5, true),
('770e8400-e29b-41d4-a716-446655440002', 'After Hours Access', 'Alert for any detection outside business hours', 'time_restriction',
    '{"time_range": {"start": "18:00", "end": "08:00"}, "days": ["monday", "tuesday", "wednesday", "thursday", "friday"], "min_confidence": 0.7}'::jsonb,
    '{"webhook": "https://security.company.com/after-hours", "sms": ["+1234567890"]}'::jsonb,
    7, true),
('770e8400-e29b-41d4-a716-446655440003', 'Server Room Unauthorized', 'Alert for non-security in server room', 'geofence',
    '{"cameras": ["550e8400-e29b-41d4-a716-446655440003"], "exclude_types": ["security"], "min_confidence": 0.75}'::jsonb,
    '{"webhook": "https://security.company.com/server-room", "email": ["it-security@company.com"]}'::jsonb,
    9, true);

-- Insert sample users
INSERT INTO users (user_id, username, email, password_hash, full_name, role, department, is_active) VALUES
('880e8400-e29b-41d4-a716-446655440000', 'admin', 'admin@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'System Administrator', 'admin', 'IT', true),
('880e8400-e29b-41d4-a716-446655440001', 'operator1', 'operator@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'Security Operator', 'operator', 'Security', true),
('880e8400-e29b-41d4-a716-446655440002', 'viewer1', 'viewer@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'Security Viewer', 'viewer', 'Security', true),
('880e8400-e29b-41d4-a716-446655440003', 'auditor', 'auditor@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'Compliance Auditor', 'auditor', 'Compliance', true);

-- Generate sample sightings for the last 7 days
DO $$
DECLARE
    camera_ids UUID[] := ARRAY[
        '550e8400-e29b-41d4-a716-446655440000',
        '550e8400-e29b-41d4-a716-446655440001',
        '550e8400-e29b-41d4-a716-446655440002',
        '550e8400-e29b-41d4-a716-446655440003'
    ];
    subject_ids UUID[] := ARRAY[
        '660e8400-e29b-41d4-a716-446655440000',
        '660e8400-e29b-41d4-a716-446655440001',
        '660e8400-e29b-41d4-a716-446655440002',
        '660e8400-e29b-41d4-a716-446655440003',
        '660e8400-e29b-41d4-a716-446655440004'
    ];
    i INTEGER;
    random_camera UUID;
    random_subject UUID;
    random_time TIMESTAMP WITH TIME ZONE;
BEGIN
    FOR i IN 1..500 LOOP
        random_camera := camera_ids[1 + floor(random() * array_length(camera_ids, 1))];
        random_subject := subject_ids[1 + floor(random() * array_length(subject_ids, 1))];
        random_time := NOW() - (random() * INTERVAL '7 days');
        
        INSERT INTO sightings (subject_id, camera_id, detection_confidence, recognition_confidence, match_distance, detected_at, scene_analysis)
        VALUES (
            random_subject,
            random_camera,
            0.7 + random() * 0.3,
            0.6 + random() * 0.4,
            random() * 0.5,
            random_time,
            jsonb_build_object(
                'crowd_density', floor(random() * 10),
                'lighting', CASE WHEN random() > 0.5 THEN 'good' ELSE 'poor' END,
                'weather_tags', ARRAY['indoor']
            )
        );
    END LOOP;
END $$;

-- Generate sample alert logs
INSERT INTO alert_logs (rule_id, subject_id, camera_id, trigger_data, status, priority, created_at)
SELECT 
    '770e8400-e29b-41d4-a716-446655440000',
    '660e8400-e29b-41d4-a716-446655440005',
    '550e8400-e29b-41d4-a716-446655440000',
    jsonb_build_object(
        'detection_confidence', 0.92,
        'location', 'Main Entrance',
        'banned_reason', 'trespassing'
    ),
    CASE WHEN random() > 0.7 THEN 'open' ELSE 'resolved' END,
    10,
    NOW() - (random() * INTERVAL '24 hours')
FROM generate_series(1, 20);

-- Insert sample audit logs
INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, ip_address, compliance_context)
SELECT 
    '880e8400-e29b-41d4-a716-446655440001',
    'view_subject',
    'subject',
    '660e8400-e29b-41d4-a716-446655440000',
    jsonb_build_object('search_query', 'john'),
    '192.168.1.100'::inet,
    jsonb_build_object('lawful_basis', 'legitimate_interest', 'retention_days', 90)
FROM generate_series(1, 50);

-- Update statistics
ANALYZE cameras;
ANALYZE subjects;
ANALYZE sightings;
ANALYZE alert_logs;
ANALYZE audit_logs;
