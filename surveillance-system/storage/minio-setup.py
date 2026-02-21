#!/usr/bin/env python3
"""
MinIO Storage Setup Script
Configures buckets, lifecycle policies, and access controls for surveillance data.
"""

import os
import json
from minio import Minio
from minio.error import S3Error
from minio.lifecycleconfig import LifecycleConfig, Rule, Filter, Expiration, Transition


def get_minio_client() -> Minio:
    """Create MinIO client from environment variables."""
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
    
    return Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure
    )


def create_bucket(client: Minio, bucket_name: str) -> None:
    """Create bucket if it doesn't exist."""
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"✓ Created bucket: {bucket_name}")
        else:
            print(f"✓ Bucket already exists: {bucket_name}")
    except S3Error as e:
        print(f"✗ Error creating bucket {bucket_name}: {e}")


def set_bucket_policy(client: Minio, bucket_name: str, policy: dict) -> None:
    """Set bucket policy."""
    try:
        client.set_bucket_policy(bucket_name, json.dumps(policy))
        print(f"✓ Set policy for bucket: {bucket_name}")
    except S3Error as e:
        print(f"✗ Error setting policy for {bucket_name}: {e}")


def setup_lifecycle_policy(client: Minio, bucket_name: str) -> None:
    """Setup lifecycle policy for bucket."""
    try:
        # Define lifecycle rules
        rules = []
        
        # Rule 1: Delete temp files after 1 day
        if bucket_name == "surveillance-temp":
            rules.append(Rule(
                status="Enabled",
                rule_id="delete-temp-files",
                filter=Filter(prefix=""),
                expiration=Expiration(days=1)
            ))
        
        # Rule 2: Transition live footage to archive after 7 days
        if bucket_name == "surveillance-live":
            rules.append(Rule(
                status="Enabled",
                rule_id="transition-to-archive",
                filter=Filter(prefix=""),
                transition=Transition(
                    days=7,
                    storage_class="COLD"
                )
            ))
            rules.append(Rule(
                status="Enabled",
                rule_id="delete-old-live",
                filter=Filter(prefix=""),
                expiration=Expiration(days=90)
            ))
        
        # Rule 3: Transition archive to glacier after 90 days
        if bucket_name == "surveillance-archive":
            rules.append(Rule(
                status="Enabled",
                rule_id="transition-to-glacier",
                filter=Filter(prefix=""),
                transition=Transition(
                    days=90,
                    storage_class="GLACIER"
                )
            ))
        
        if rules:
            config = LifecycleConfig(rules)
            client.set_bucket_lifecycle(bucket_name, config)
            print(f"✓ Set lifecycle policy for bucket: {bucket_name}")
            
    except S3Error as e:
        print(f"✗ Error setting lifecycle policy for {bucket_name}: {e}")


def setup_versioning(client: Minio, bucket_name: str) -> None:
    """Enable versioning for important buckets."""
    try:
        if bucket_name in ["surveillance-subjects", "surveillance-archive"]:
            client.set_bucket_versioning(
                bucket_name,
                config={"Status": "Enabled"}
            )
            print(f"✓ Enabled versioning for bucket: {bucket_name}")
    except S3Error as e:
        print(f"✗ Error enabling versioning for {bucket_name}: {e}")


def create_folder_structure(client: Minio, bucket_name: str) -> None:
    """Create initial folder structure in bucket."""
    try:
        folders = {
            "surveillance-live": ["camera-001/", "camera-002/", "camera-003/", "camera-004/"],
            "surveillance-subjects": ["known/", "unknown/", "profiles/"],
            "surveillance-archive": ["compressed/", "backup/"],
            "surveillance-temp": ["processing/", "uploads/"]
        }
        
        if bucket_name in folders:
            for folder in folders[bucket_name]:
                # MinIO doesn't have real folders, create placeholder object
                client.put_object(
                    bucket_name,
                    f"{folder}.keep",
                    data=b"",
                    length=0,
                    content_type="application/x-directory"
                )
            print(f"✓ Created folder structure for bucket: {bucket_name}")
            
    except S3Error as e:
        print(f"✗ Error creating folder structure for {bucket_name}: {e}")


def main():
    """Main setup function."""
    print("=" * 60)
    print("MinIO Storage Setup for Surveillance System")
    print("=" * 60)
    
    client = get_minio_client()
    
    # Define buckets
    buckets = [
        "surveillance-live",      # Hot storage: Last 7 days
        "surveillance-subjects",  # Subject images and embeddings
        "surveillance-archive",   # Warm storage: 7-90 days
        "surveillance-temp"       # Transient processing files
    ]
    
    # Bucket policies (read-write for surveillance system)
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::%s" % buckets[0],
                    "arn:aws:s3:::%s/*" % buckets[0]
                ]
            }
        ]
    }
    
    # Create and configure each bucket
    for bucket in buckets:
        print(f"\n--- Configuring bucket: {bucket} ---")
        create_bucket(client, bucket)
        set_bucket_policy(client, bucket, bucket_policy)
        setup_lifecycle_policy(client, bucket)
        setup_versioning(client, bucket)
        create_folder_structure(client, bucket)
    
    print("\n" + "=" * 60)
    print("MinIO setup completed!")
    print("=" * 60)
    print("\nBucket Structure:")
    print("  surveillance-live/     - Hot storage (SSD): Last 7 days")
    print("  surveillance-subjects/ - Subject images and embeddings")
    print("  surveillance-archive/  - Warm storage (HDD): 7-90 days")
    print("  surveillance-temp/     - Transient files (24h TTL)")


if __name__ == "__main__":
    main()
