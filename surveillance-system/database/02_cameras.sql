-- ============================================================
-- Camera Configuration Table
-- Stores IPTV camera metadata and stream configuration
-- ============================================================

CREATE TABLE cameras (
    camera_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    location VARCHAR(500),
    rtsp_url TEXT NOT NULL,
    stream_config JSONB DEFAULT '{
        "protocol": "rtsp",
        "resolution": "1920x1080",
        "fps": 15,
        "codec": "h264",
        "auth_type": "basic"
    }'::jsonb,
    detection_zones JSONB, -- Polygon coordinates for ROI
    is_active BOOLEAN DEFAULT true,
    health_status VARCHAR(50) DEFAULT 'unknown',
    last_frame_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_health_status CHECK (health_status IN ('healthy', 'degraded', 'disconnected', 'unknown', 'error'))
);

-- Indexes for cameras
CREATE INDEX idx_cameras_active ON cameras(is_active);
CREATE INDEX idx_cameras_health ON cameras(health_status);
CREATE INDEX idx_cameras_location ON cameras USING gin(location gin_trgm_ops);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_cameras_updated_at
    BEFORE UPDATE ON cameras
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE cameras IS 'IPTV surveillance camera configuration and metadata';
COMMENT ON COLUMN cameras.stream_config IS 'JSON configuration: protocol, resolution, fps, codec, auth_type';
COMMENT ON COLUMN cameras.detection_zones IS 'Array of polygon coordinates defining regions of interest';
COMMENT ON COLUMN cameras.health_status IS 'Current stream health: healthy, degraded, disconnected, unknown, error';
