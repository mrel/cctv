-- ============================================================
-- IPTV Facial Recognition Surveillance System
-- Database Schema - Extensions Setup
-- PostgreSQL 15+ with pgvector 0.5+
-- ============================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extensions
SELECT * FROM pg_extension WHERE extname IN ('uuid-ossp', 'vector');
