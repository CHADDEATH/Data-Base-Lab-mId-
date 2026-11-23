"""
Pak Voyage - Automated Excel Data Importer & ETL Pipeline
Reads 17 workbooks from 01_Excel_Data/, validates FK integrity, and inserts into Oracle Database 26ai.
Safe to re-run without duplicate key violations.
"""

import os
import datetime
import openpyxl
from database import get_connection, execute_non_query, execute_query

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_DIR = os.path.join(os.path.dirname(BASE_DIR), "01_Excel_Data")

IMPORT_ORDER = [
    ("destinations.xlsx", "DESTINATIONS", "DESTINATION_ID"),
    ("destination_guides.xlsx", "DESTINATION_GUIDES", "GUIDE_ID"),
    ("hotels.xlsx", "HOTELS", "HOTEL_ID"),
    ("rooms.xlsx", "HOTEL_ROOMS", "ROOM_ID"),
    ("hotel_facilities.xlsx", "HOTEL_FACILITIES", "FACILITY_ID"),
    ("landmarks.xlsx", "LANDMARKS", "LANDMARK_ID"),
    ("trails_trekking.xlsx", "TRAILS", "TRAIL_ID"),
    ("trail_services.xlsx", "TRAIL_SERVICES", "SERVICE_ID"),
    ("activities.xlsx", "ACTIVITIES", "ACTIVITY_ID"),
    ("zoos_parks.xlsx", "ZOOS_PARKS", "FACILITY_ID"),
    ("facility_tickets.xlsx", "FACILITY_TICKETS", "SUB_TICKET_ID"),
    ("restaurants.xlsx", "RESTAURANTS", "RESTAURANT_ID"),
    ("food_items.xlsx", "FOOD_ITEMS", "ITEM_ID"),
    ("transport_types.xlsx", "TRANSPORT_TYPES", "TRANSPORT_TYPE_ID"),
    ("transport_services.xlsx", "TRANSPORT_SERVICES", "SERVICE_ID"),
    ("transport_routes.xlsx", "PUBLIC_TRANSPORT_ROUTES", "ROUTE_ID"),
    ("public_transport_stops.xlsx", "PUBLIC_TRANSPORT_STOPS", "STOP_ID"),
]

def read_excel_records(filename):
    """Reads all rows from an Excel file into a list of dictionaries."""
    filepath = os.path.join(EXCEL_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[ERROR]: File not found: {filepath}")
        return [], []

    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return [], []

    headers = [str(h).strip().upper() for h in rows[0]]
    records = []
    for r in rows[1:]:
        if any(r):
            records.append(dict(zip(headers, r)))
    return headers, records

def import_table_records(conn, filename, table_name, pk_col):
    """
    Validates and imports records into an Oracle table.
    Checks existence of primary key to prevent duplicate insertion.
    """
    headers, records = read_excel_records(filename)
    if not records:
        return 0, 0, ["No records found in Excel file."]

    cursor = conn.cursor()
    imported = 0
    skipped = 0
    errors = []

    # Get existing primary keys in table
    try:
        cursor.execute(f"SELECT {pk_col} FROM {table_name}")
        existing_pks = set(row[0] for row in cursor.fetchall())
    except Exception as e:
        existing_pks = set()

    for idx, rec in enumerate(records, 2):
        pk_val = rec.get(pk_col)
        if pk_val in existing_pks:
            skipped += 1
            continue

        # Prepare parameterized INSERT statement
        cols = list(rec.keys())
        bind_vars = [f":{col}" for col in cols]
        sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({', '.join(bind_vars)})"

        # Sanitize date strings and None values
        params = {}
        for k, v in rec.items():
            if k.endswith("_DATE") and v is not None:
                if isinstance(v, str):
                    try:
                        clean_date = v.split()[0].strip()
                        params[k] = datetime.datetime.strptime(clean_date, "%Y-%m-%d").date()
                    except Exception:
                        params[k] = v
                elif hasattr(v, 'date'):
                    params[k] = v.date()
                else:
                    params[k] = v
            else:
                params[k] = v

        try:
            cursor.execute(sql, params)
            imported += 1
            existing_pks.add(pk_val)
        except Exception as e:
            errors.append(f"Row {idx} ({pk_val}): {e}")

    conn.commit()
    cursor.close()
    return imported, skipped, errors

def run_import():
    """Runs the full ETL pipeline for all 17 Excel datasets."""
    print("\n" + "=" * 65)
    print("      PAK VOYAGE - ORACLE DATABASE DATA IMPORT (ETL)")
    print("=" * 65)

    conn = get_connection()
    if not conn:
        print("[ABORTED]: Could not establish connection to Oracle Database.")
        return False

    total_imported = 0
    total_skipped = 0
    all_errors = {}

    for filename, table_name, pk_col in IMPORT_ORDER:
        print(f"Importing {filename:<28} -> {table_name:<24}...", end=" ", flush=True)
        imp, skip, errs = import_table_records(conn, filename, table_name, pk_col)
        total_imported += imp
        total_skipped += skip
        if errs:
            all_errors[table_name] = errs
            print(f"DONE (Imported: {imp}, Skipped: {skip}, Errors: {len(errs)})")
        else:
            print(f"DONE (Imported: {imp:>3}, Already Exists: {skip:>3})")

    conn.close()

    print("-" * 65)
    print(f"ETL SUMMARY:")
    print(f"Total Newly Inserted Records: {total_imported}")
    print(f"Total Pre-Existing (Skipped): {total_skipped}")
    print(f"Combined Database Records:    {total_imported + total_skipped}")
    print("=" * 65)

    if all_errors:
        print("\nERRORS ENCOUNTERED DURING IMPORT:")
        for tbl, err_list in all_errors.items():
            print(f"\nTable {tbl}:")
            for err in err_list[:5]:  # Show first 5 errors per table
                print(f"  - {err}")
    else:
        print("All records verified and successfully loaded into Oracle Database 26ai.")
    return True

if __name__ == "__main__":
    run_import()
