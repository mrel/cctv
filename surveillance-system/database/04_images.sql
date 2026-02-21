-- ============================================================
-- Image Asset Registry Table
-- Stores metadata for all captured images and face crops
-- ============================================================

CREATE TABLE images (
    image_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subject_id UUID REFERENCES subjects(subject_id) ON DELETE SET NULL,
    camera_id UUID REFERENCES cameras(camera_id) ON DELETE SET NULL,
    storage_path VARCHAR(500) NOT NULL, -- MinIO path: subjects/uuid/image.jpg
    storage_bucket VARCHAR(100) DEFAULT 'surveillance-images',
    image_type VARCHAR(50), -- 'full_frame', 'face_crop', 'thumbnail'
    file_size_bytes INTEGER,
    checksum VARCHAR(64), -- SHA-256 for integrity verification
    resolution VARCHAR(20), -- e.g., "1920x1080"
    quality_score FLOAT CHECK (quality_score >= 0.0 AND quality_score <= 1.0), -- Blur detection
    bounding_box JSONB, -- {"x": 120, "y": 340, "w": 100, "h": 120}
    landmarks JSONB, -- Facial keypoints for verification
    captured_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_image_type CHECK (image_type IN ('full_frame', 'face_crop', 'thumbnail', 'profile')),
    CONSTRAINT valid_quality_score CHECK (quality_score >= 0.0 AND quality_score <= 1.0)
);

-- Indexes for images
CREATE INDEX idx_images_subject ON images(subject_id);
CREATE INDEX idx_images_camera ON images(camera_id);
CREATE INDEX idx_images_type ON images(image_type);
CREATE INDEX idx_images_captured_at ON images(captured_at DESC);
CREATE INDEX idx_images_camera_captured ON images(camera_id, captured_at DESC);
CREATE INDEX idx_images_quality ON images(quality_score) WHERE quality_score IS NOT NULL;

-- Composite index for gallery queries
CREATE INDEX idx_images_subject_type ON images(subject_id, image_type, captured_at DESC);

-- Comments
COMMENT ON TABLE images IS 'Registry of all captured images with metadata and storage locations';
COMMENT ON COLUMN images.storage_path IS 'MinIO object storage path';
COMMENT ON COLUMN images.quality_score IS 'Image quality score 0.0-1.0 based on blur detection';
COMMENT ON COLUMN images.bounding_box IS 'Face detection bounding box coordinates';
COMMENT ON COLUMN images.landmarks IS 'Facial landmarks for verification (eyes, nose, mouth)';
