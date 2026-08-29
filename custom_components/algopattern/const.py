"""Constants for the AlgoPattern Home Assistant integration."""

DOMAIN = "algopattern"
DEFAULT_NAME = "AlgoPattern"

# Config entries keys
CONF_ACCESS_TOKEN = "access_token"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_USER_ID = "user_id"
CONF_EMAIL = "email"
CONF_NAME = "name"
CONF_PASSWORD = "password"
CONF_EXPIRES_AT = "expires_at"

# AlgoPattern server Production Endpoints
SUPABASE_URL = "https://zxziakgfedyoosmjtaoq.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_ACQcm74_0UFOdsDNT4nPnA_fgDJLEIs"

# Polling interval (5 minutes)
DEFAULT_SCAN_INTERVAL = 300

# Sensor Keys
SENSOR_STREAK_LENGTH = "streak_length"
SENSOR_XP = "xp"
SENSOR_FREEZES_AVAILABLE = "freezes_available"
SENSOR_TOTAL_ACTIVE_DAYS = "total_active_days"
SENSOR_LAST_ACTIVE_DATE = "last_active_date"
SENSOR_QUIZZES_COMPLETED = "quizzes_completed"
SENSOR_EXPERIENCE_LEVEL = "experience_level"
SENSOR_PREPARATION_GOAL = "preparation_goal"
SENSOR_DAILY_REMINDER_TIME = "daily_reminder_time"
SENSOR_USER_ID = "user_id"
SENSOR_USER_NAME = "name"

# Binary Sensor Keys
BINARY_SENSOR_COMPLETED_TODAY = "completed_today"
BINARY_SENSOR_ACTIVE_TODAY = "active_today"
BINARY_SENSOR_IS_PRO = "is_pro"
BINARY_SENSOR_DAILY_REMINDER_ENABLED = "daily_reminder_enabled"
BINARY_SENSOR_IMMEDIATE_FEEDBACK = "immediate_quiz_feedback"
