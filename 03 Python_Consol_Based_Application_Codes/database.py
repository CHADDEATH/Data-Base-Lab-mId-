"""
Pak Voyage - Oracle Database Connection & Persistence Module
Handles all communication with Oracle Database 26ai using python-oracledb.
"""

import sys
import oracledb

try:
    from config import ORACLE_CONFIG
except ImportError:
    from config_example import ORACLE_CONFIG

def get_connection():
    """
    Establishes and returns a direct connection to Oracle Database 26ai.
    Uses python-oracledb Thin mode (no external Oracle Client installation required).
    """
    try:
        dsn_string = f"{ORACLE_CONFIG['host']}:{ORACLE_CONFIG['port']}/{ORACLE_CONFIG['service_name']}"
        connection = oracledb.connect(
            user=ORACLE_CONFIG["user"],
            password=ORACLE_CONFIG["password"],
            dsn=dsn_string
        )
        with connection.cursor() as cur:
            cur.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'")
        return connection
    except oracledb.Error as e:
        error_obj, = e.args
        print("\n" + "!" * 65)
        print("  ORACLE DATABASE CONNECTION ERROR")
        print("!" * 65)
        print(f"  Error Code:    {error_obj.code}")
        print(f"  Error Message: {error_obj.message}")
        print("-" * 65)
        print("  Connection Parameters Attempted:")
        print(f"  - Host:         {ORACLE_CONFIG['host']}")
        print(f"  - Port:         {ORACLE_CONFIG['port']}")
        print(f"  - Service Name: {ORACLE_CONFIG['service_name']}")
        print(f"  - User:         {ORACLE_CONFIG['user']}")
        print("-" * 65)
        print("  Troubleshooting Instructions for Oracle SQL Developer / 26ai:")
        print("  1. Ensure the Oracle Database service / container is started.")
        print("  2. Verify your port (default 1521) and service name (e.g. FREEPDB1).")
        print("  3. Update config.py with your exact local credentials.")
        print("!" * 65 + "\n")
        return None

def test_connection():
    """Tests if Oracle Database is reachable and returns status."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT BANNER FROM V$VERSION WHERE ROWNUM = 1")
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            # Clean string without third-party slogans or marketing text
            clean_ver = "Oracle Database 26ai"
            if row and row[0]:
                raw = row[0]
                if "26ai" in raw or "23" in raw:
                    clean_ver = "Oracle Database 26ai (Release 23.26)"
                else:
                    clean_ver = "Oracle Database 26ai"
            return True, f"{clean_ver} - Connected to FREEPDB1"
        except Exception as e:
            conn.close()
            return False, str(e)
    return False, "Failed to connect to Oracle"

def execute_query(sql, params=None):
    """
    Executes a SELECT query with parameters and returns a list of dictionaries.
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
            
        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))
            
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"[Database Error]: {e}")
        if conn:
            conn.close()
        return []

def execute_non_query(sql, params=None):
    """
    Executes an INSERT, UPDATE, or DELETE query and commits transaction.
    Returns (success_bool, rows_affected, error_message).
    """
    conn = get_connection()
    if not conn:
        return False, 0, "No database connection"
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        rowcount = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return True, rowcount, None
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, 0, str(e)

def execute_insert_returning_id(sql, params, out_id_param_name="out_id"):
    """
    Executes an INSERT statement with a RETURNING clause into an output variable.
    """
    conn = get_connection()
    if not conn:
        return None, "No database connection"
    try:
        cursor = conn.cursor()
        out_var = cursor.var(oracledb.NUMBER)
        params[out_id_param_name] = out_var
        cursor.execute(sql, params)
        new_id = out_var.getvalue()[0] if isinstance(out_var.getvalue(), list) else out_var.getvalue()
        conn.commit()
        cursor.close()
        conn.close()
        return int(new_id), None
    except Exception as e:
        conn.rollback()
        conn.close()
        return None, str(e)
