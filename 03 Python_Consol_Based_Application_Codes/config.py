"""
Pak Voyage - Local Database Configuration
Used by python-oracledb for direct connectivity to Oracle Database 26ai.
"""

import os

# Oracle 26ai Connection Parameters
# Can be overridden via environment variables if desired
ORACLE_CONFIG = {
    "user": os.environ.get("PV_DB_USER", "SYSTEM"),
    "password": os.environ.get("PV_DB_PASSWORD", "11034"),
    "host": os.environ.get("PV_DB_HOST", "localhost"),
    "port": int(os.environ.get("PV_DB_PORT", "1521")),
    "service_name": os.environ.get("PV_DB_SERVICE", "FREEPDB1")
}

DEFAULT_ADMIN = {
    "username": "bilal",
    "password": "ROMAN"
}
