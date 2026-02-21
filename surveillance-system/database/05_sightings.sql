-- ============================================================
-- High-Volume Sightings Table (Time-Series)
-- Partitioned by month for efficient time-range queries
-- ============================================================

-- Main partitioned table
CREATE TABLE sightings (
    sighting_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subject_id UUID REFERENCES subjects(subject_id) ON DELETE SET NULL,
    camera_id UUID REFERENCES cameras(camera_id) ON DELETE SET NULL,
    image_id UUID REFERENCES images(image_id) ON DELETE SET NULL,
    detection_confidence FLOAT NOT NULL CHECK (detection_confidence >= 0.0 AND detection_confidence <= 1.0),
    recognition_confidence FLOAT CHECK (recognition_confidence >= 0.0 AND recognition_confidence <= 1.0),
    match_distance FLOAT, -- Vector distance metric (lower is better match)
    scene_analysis JSONB, -- crowd_density, lighting, weather_tags
    detected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_detection_confidence CHECK (detection_confidence >= 0.0 AND detection_confidence <= 1.0),
    CONSTRAINT valid_recognition_confidence CHECK (recognition_confidence >= 0.0 AND recognition_confidence <= 1.0)
) PARTITION BY RANGE (detected_at);

-- Create partitions for 2024-2026 (auto-creation recommended for production)
-- 2024 partitions
CREATE TABLE sightings_y2024m01 PARTITION OF sightings
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE sightings_y2024m02 PARTITION OF sightings
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
CREATE TABLE sightings_y2024m03 PARTITION OF sightings
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');
CREATE TABLE sightings_y2024m04 PARTITION OF sightings
    FOR VALUES FROM ('2024-04-01') TO ('2024-05-01');
CREATE TABLE sightings_y2024m05 PARTITION OF sightings
    FOR VALUES FROM ('2024-05-01') TO ('2024-06-01');
CREATE TABLE sightings_y2024m06 PARTITION OF sightings
    FOR VALUES FROM ('2024-06-01') TO ('2024-07-01');
CREATE TABLE sightings_y2024m07 PARTITION OF sightings
    FOR VALUES FROM ('2024-07-01') TO ('2024-08-01');
CREATE TABLE sightings_y2024m08 PARTITION OF sightings
    FOR VALUES FROM ('2024-08-01') TO ('2024-09-01');
CREATE TABLE sightings_y2024m09 PARTITION OF sightings
    FOR VALUES FROM ('2024-09-01') TO ('2024-10-01');
CREATE TABLE sightings_y2024m10 PARTITION OF sightings
    FOR VALUES FROM ('2024-10-01') TO ('2024-11-01');
CREATE TABLE sightings_y2024m11 PARTITION OF sightings
    FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');
CREATE TABLE sightings_y2024m12 PARTITION OF sightings
    FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

-- 2025 partitions
CREATE TABLE sightings_y2025m01 PARTITION OF sightings
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE sightings_y2025m02 PARTITION OF sightings
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE sightings_y2025m03 PARTITION OF sightings
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
CREATE TABLE sightings_y2025m04 PARTITION OF sightings
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
CREATE TABLE sightings_y2025m05 PARTITION OF sightings
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');
CREATE TABLE sightings_y2025m06 PARTITION OF sightings
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');
CREATE TABLE sightings_y2025m07 PARTITION OF sightings
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');
CREATE TABLE sightings_y2025m08 PARTITION OF sightings
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
CREATE TABLE sightings_y2025m09 PARTITION OF sightings
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
CREATE TABLE sightings_y2025m10 PARTITION OF sightings
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
CREATE TABLE sightings_y2025m11 PARTITION OF sightings
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
CREATE TABLE sightings_y2025m12 PARTITION OF sightings
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- 2026 partitions
CREATE TABLE sightings_y2026m01 PARTITION OF sightings
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE sightings_y2026m02 PARTITION OF sightings
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
CREATE TABLE sightings_y2026m03 PARTITION OF sightings
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
CREATE TABLE sightings_y2026m04 PARTITION OF sightings
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');
CREATE TABLE sightings_y2026m05 PARTITION OF sightings
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');
CREATE TABLE sightings_y2026m06 PARTITION OF sightings
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');

-- Default partition for any data outside defined ranges
CREATE TABLE sightings_default PARTITION OF sightings DEFAULT;

-- Indexes for sightings (applied to all partitions)
CREATE INDEX idx_sightings_time ON sightings(detected_at DESC);
CREATE INDEX idx_sightings_subject_time ON sightings(subject_id, detected_at DESC);
CREATE INDEX idx_sightings_camera ON sightings(camera_id, detected_at DESC);
CREATE INDEX idx_sightings_camera_time ON sightings(camera_id, detected_at DESC);
CREATE INDEX idx_sightings_confidence ON sightings(detection_confidence) WHERE detection_confidence > 0.8;

-- Partial index for high-confidence sightings (common query pattern)
CREATE INDEX idx_sightings_high_confidence ON sightings(subject_id, detected_at DESC)
    WHERE recognition_confidence > 0.7;

-- Comments
COMMENT ON TABLE sightings IS 'Time-series table of all face detections with recognition results';
COMMENT ON COLUMN sightings.match_distance IS 'Vector distance between detected face and matched subject (lower = better match)';
COMMENT ON COLUMN sightings.scene_analysis IS 'Contextual data: crowd density, lighting conditions, weather tags';
