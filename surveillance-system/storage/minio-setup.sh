#!/bin/bash
# ============================================================
# MinIO Bucket Setup Script
# Configures buckets and policies using mc (MinIO Client)
# ============================================================

set -e

# Configuration
MINIO_ENDPOINT="${MINIO_ENDPOINT:-http://localhost:9000}"
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-minioadmin}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-minioadmin}"
ALIAS="surveillance"

echo "========================================"
echo "MinIO Storage Setup"
echo "========================================"
echo "Endpoint: $MINIO_ENDPOINT"
echo ""

# Check if mc is installed
if ! command -v mc &> /dev/null; then
    echo "Error: MinIO Client (mc) not found. Please install it first."
    echo "Download: https://min.io/docs/minio/linux/reference/minio-mc.html"
    exit 1
fi

# Configure MinIO alias
echo "Configuring MinIO alias..."
mc alias set $ALIAS $MINIO_ENDPOINT $MINIO_ACCESS_KEY $MINIO_SECRET_KEY --api s3v4

# Create buckets
echo ""
echo "Creating buckets..."

BUCKETS=(
    "surveillance-live"
    "surveillance-subjects"
    "surveillance-archive"
    "surveillance-temp"
)

for bucket in "${BUCKETS[@]}"; do
    echo "  Creating bucket: $bucket"
    mc mb --ignore-existing $ALIAS/$bucket
done

# Set bucket policies
echo ""
echo "Setting bucket policies..."

# surveillance-live: Public read, authenticated write
mc anonymous set download $ALIAS/surveillance-live

# surveillance-subjects: Private (default)
mc anonymous set none $ALIAS/surveillance-subjects

# surveillance-archive: Private
mc anonymous set none $ALIAS/surveillance-archive

# surveillance-temp: Private, auto-delete
mc anonymous set none $ALIAS/surveillance-temp

# Create folder structure
echo ""
echo "Creating folder structure..."

# Live footage folders
for i in {001..010}; do
    mc mb --ignore-existing $ALIAS/surveillance-live/camera-$i
    mc mb --ignore-existing $ALIAS/surveillance-live/camera-$i/$(date +%Y%m%d)
done

# Subject folders
mc mb --ignore-existing $ALIAS/surveillance-subjects/known
mc mb --ignore-existing $ALIAS/surveillance-subjects/unknown
mc mb --ignore-existing $ALIAS/surveillance-subjects/profiles

# Archive folders
mc mb --ignore-existing $ALIAS/surveillance-archive/compressed
mc mb --ignore-existing $ALIAS/surveillance-archive/backup

# Temp folders
mc mb --ignore-existing $ALIAS/surveillance-temp/processing
mc mb --ignore-existing $ALIAS/surveillance-temp/uploads

# Set lifecycle policies (if supported)
echo ""
echo "Setting lifecycle policies..."

# Create lifecycle policy for temp bucket (1 day retention)
cat > /tmp/temp-lifecycle.json << 'EOF'
{
    "Rules": [
        {
            "ID": "delete-temp-files",
            "Status": "Enabled",
            "Filter": {
                "Prefix": ""
            },
            "Expiration": {
                "Days": 1
            }
        }
    ]
}
EOF

mc ilm import $ALIAS/surveillance-temp < /tmp/temp-lifecycle.json 2>/dev/null || echo "  Lifecycle policy skipped (may require newer MinIO version)"

# Create lifecycle policy for live bucket (90 day retention)
cat > /tmp/live-lifecycle.json << 'EOF'
{
    "Rules": [
        {
            "ID": "archive-old-footage",
            "Status": "Enabled",
            "Filter": {
                "Prefix": ""
            },
            "Transition": [
                {
                    "Days": 7,
                    "StorageClass": "COLD"
                }
            ],
            "Expiration": {
                "Days": 90
            }
        }
    ]
}
EOF

mc ilm import $ALIAS/surveillance-live < /tmp/live-lifecycle.json 2>/dev/null || echo "  Lifecycle policy skipped (may require newer MinIO version)"

# Enable versioning for subjects and archive
echo ""
echo "Enabling versioning..."
mc version enable $ALIAS/surveillance-subjects 2>/dev/null || echo "  Versioning skipped for subjects"
mc version enable $ALIAS/surveillance-archive 2>/dev/null || echo "  Versioning skipped for archive"

# Cleanup temp files
rm -f /tmp/temp-lifecycle.json /tmp/live-lifecycle.json

# Verify setup
echo ""
echo "========================================"
echo "Verifying setup..."
echo "========================================"
mc ls $ALIAS/

echo ""
echo "========================================"
echo "MinIO setup completed successfully!"
echo "========================================"
echo ""
echo "Bucket Structure:"
echo "  surveillance-live/     - Hot storage: Last 7 days"
echo "  surveillance-subjects/ - Subject images and embeddings"
echo "  surveillance-archive/  - Warm storage: 7-90 days"
echo "  surveillance-temp/     - Transient files (24h TTL)"
echo ""
echo "Storage Tiers:"
echo "  Hot (SSD):    surveillance-live (last 7 days)"
echo "  Warm (HDD):   surveillance-archive (7-90 days)"
echo "  Cold:         >90 days with compression"
