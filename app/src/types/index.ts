/**
 * TypeScript type definitions for the Surveillance System
 */

// Camera types
export interface Camera {
  camera_id: string;
  name: string;
  location?: string;
  rtsp_url: string;
  stream_config: StreamConfig;
  detection_zones?: DetectionZone[];
  is_active: boolean;
  health_status: 'healthy' | 'degraded' | 'disconnected' | 'unknown' | 'error';
  last_frame_at?: string;
  created_at: string;
  updated_at: string;
}

export interface StreamConfig {
  protocol: string;
  resolution: string;
  fps: number;
  codec: string;
  auth_type: string;
}

export interface DetectionZone {
  x: number;
  y: number;
  w: number;
  h: number;
}

// Subject types
export interface Subject {
  subject_id: string;
  label?: string;
  subject_type: 'employee' | 'visitor' | 'banned' | 'vip' | 'unknown';
  status: 'active' | 'inactive' | 'archived';
  enrollment_date: string;
  last_seen?: string;
  metadata?: SubjectMetadata;
  consent_status: 'granted' | 'denied' | 'pending' | 'withdrawn';
  retention_until?: string;
  image_count: number;
  sighting_count: number;
}

export interface SubjectMetadata {
  estimated_age?: number;
  gender?: string;
  ethnicity?: string;
  department?: string;
  clothing_preferences?: string[];
}

// Sighting types
export interface Sighting {
  sighting_id: string;
  subject_id?: string;
  camera_id: string;
  image_id?: string;
  detection_confidence: number;
  recognition_confidence?: number;
  match_distance?: number;
  scene_analysis?: SceneAnalysis;
  detected_at: string;
  processed_at: string;
  is_recognized: boolean;
  is_high_confidence: boolean;
}

export interface SceneAnalysis {
  crowd_density?: number;
  lighting?: string;
  weather_tags?: string[];
}

// Alert types
export interface AlertRule {
  rule_id: string;
  name: string;
  description?: string;
  rule_type: 'blacklist' | 'whitelist' | 'geofence' | 'loitering' | 'tailgating' | 'crowd' | 'time_restriction' | 'custom';
  conditions: AlertConditions;
  actions?: AlertActions;
  is_active: boolean;
  priority: number;
  cooldown_seconds: number;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface AlertConditions {
  subject_types?: string[];
  subject_ids?: string[];
  cameras?: string[];
  camera_zones?: any[];
  min_confidence?: number;
  time_range?: { start: string; end: string };
  days?: string[];
  exclude_types?: string[];
}

export interface AlertActions {
  webhook?: string;
  email?: string[];
  sms?: string[];
  push?: boolean;
}

export interface AlertLog {
  alert_id: string;
  rule_id?: string;
  rule_name?: string;
  rule_type?: string;
  subject_id?: string;
  subject_label?: string;
  camera_id?: string;
  camera_name?: string;
  trigger_data: any;
  status: 'open' | 'acknowledged' | 'resolved' | 'false_positive' | 'escalated';
  priority?: number;
  acknowledged_by?: string;
  acknowledged_at?: string;
  resolved_at?: string;
  notes?: string;
  created_at: string;
  age_minutes?: number;
}

// User types
export interface User {
  user_id: string;
  username: string;
  email: string;
  full_name?: string;
  role: 'admin' | 'operator' | 'viewer' | 'auditor';
  department?: string;
  is_active: boolean;
  last_login?: string;
  mfa_enabled: boolean;
  created_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
  mfa_code?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Analytics types
export interface Statistics {
  total_cameras: number;
  active_cameras: number;
  total_subjects: number;
  known_subjects: number;
  unknown_subjects: number;
  total_sightings_24h: number;
  total_alerts_24h: number;
  open_alerts: number;
  avg_detections_per_hour: number;
}

export interface HeatmapDataPoint {
  timestamp: string;
  camera_id: string;
  camera_name: string;
  detection_count: number;
  unique_subjects: number;
}

// Detection types
export interface Detection {
  id: string;
  cameraId: string;
  cameraName: string;
  subjectId?: string;
  subjectLabel?: string;
  confidence: number;
  timestamp: string;
  boundingBox: { x: number; y: number; w: number; h: number };
  imageUrl?: string;
}

// UI types
export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

export interface LayoutConfig {
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark' | 'system';
  liveViewLayout: '1x1' | '2x2' | '3x3' | '4x4';
}
