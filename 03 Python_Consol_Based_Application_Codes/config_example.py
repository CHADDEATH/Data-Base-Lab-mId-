"""
Pak Voyage - Database Configuration Example
Rename this file to config.py and fill in your Oracle Database 26ai connection details.
"""

# Oracle Database Connection Parameters
ORACLE_CONFIG = {
    "user": "pak_voyage_user",         # Your Oracle DB username
    "password": "YourSecurePassword",   # Your Oracle DB password
    "host": "localhost",               # Database host (e.g. localhost or IP)
    "port": 1521,                      # Default Oracle listener port
    "service_name": "FREEPDB1"         # Oracle 26ai default pluggable service name (e.g., FREEPDB1 or XEPDB1)
}

# Initial Administrator Credentials (Configurable)
DEFAULT_ADMIN = {
    "username": "bilal",
    "password": "ROMAN"
}
