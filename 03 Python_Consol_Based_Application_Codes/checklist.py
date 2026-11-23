"""
Pak Voyage - Travel Packing Checklist & Safety Information Module
Interactive packing checklist with completion tracking and northern mountain safety warnings.
"""

from database import execute_query, execute_non_query
from trip_planner import get_user_trips, get_trip_destinations

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

DEFAULT_CHECKLIST_ITEMS = [
    ("Original CNIC / Passport & Visa Documents", "Documents"),
    ("Printed Hotel & Transport Booking Vouchers", "Documents"),
    ("High-Altitude Insulated Thermal Clothing & Windbreaker", "Clothing"),
    ("Sturdy Hiking Boots with Ankle Support & Extra Socks", "Footwear"),
    ("First Aid Kit (Bandages, Antiseptics, Altitude AMS Medicines)", "Health"),
    ("Personal Prescription Medicines & Water Purification Tablets", "Health"),
    ("20,000mAh Power Bank & Dual-Voltage Cables", "Electronics"),
    ("Reusable Insulated Water Bottle (Hydration is Critical)", "Gear"),
    ("Polarized UV-Protection Sunglasses & High-SPF Sunscreen", "Protection"),
    ("Sufficient Cash in PKR (Mountain Towns Have Rare/Unreliable ATMs)", "Finance"),
    ("Emergency Local Contact Numbers Saved Offline", "Safety")
]

def populate_default_checklist(trip_id):
    """Inserts default items into a newly created trip."""
    for title, cat in DEFAULT_CHECKLIST_ITEMS:
        sql = """
            INSERT INTO TRIP_CHECKLIST (TRIP_ID, ITEM_TITLE, CATEGORY, IS_COMPLETED)
            VALUES (:tid, :title, :cat, 'NO')
        """
        execute_non_query(sql, {"tid": trip_id, "title": title, "cat": cat})

def get_trip_checklist(trip_id):
    """Retrieves checklist items for a trip."""
    sql = "SELECT * FROM TRIP_CHECKLIST WHERE TRIP_ID = :tid ORDER BY CHECKLIST_ID ASC"
    return execute_query(sql, {"tid": trip_id})

def display_checklist_menu(current_user):
    """Interactive checklist and safety warnings menu."""
    trips = get_user_trips(current_user["user_id"])
    if not trips:
        print("\nNo trips found. Create a trip to manage your packing checklist.")
        input("Press Enter to continue...")
        return

    while True:
        print("\n" + "=" * 65)
        print(f"      {GREEN}{BOLD}TRAVEL CHECKLIST & SAFETY GUIDE - {current_user['full_name'].upper()}{RESET}")
        print("=" * 65)
        print("Select Trip to Manage Checklist & Safety:")
        for idx, t in enumerate(trips, 1):
            print(f"  {idx}. {t['trip_name']}")
        print("0. Back to Tourist Dashboard")
        print("-" * 65)

        sel = input("Select trip: ").strip()
        if sel == "0":
            break
        try:
            t_idx = int(sel) - 1
            if 0 <= t_idx < len(trips):
                manage_trip_checklist(trips[t_idx])
            else:
                print("[ERROR]: Invalid selection.")
        except ValueError:
            print("[ERROR]: Invalid input.")

def manage_trip_checklist(trip):
    """Sub-menu for a specific trip's checklist and destination-specific alerts."""
    while True:
        items = get_trip_checklist(trip["trip_id"])
        completed_count = sum(1 for i in items if i["is_completed"] == "YES")
        total_count = len(items)

        print("\n" + "=" * 70)
        print(f"      PACKING & TRAVEL CHECKLIST: {trip['trip_name'].upper()}")
        print(f"      Progress: {completed_count} / {total_count} Completed")
        print("=" * 70)

        # Destination safety warnings
        dest_stops = get_trip_destinations(trip["trip_id"])
        has_mountain_dest = any(d["destination_id"] in (4, 5) for d in dest_stops)
        if has_mountain_dest:
            print(">>> REGIONAL HIGH-ALTITUDE & SAFETY ADVISORY <<<")
            print("  1. Acute Mountain Sickness (AMS): Drink 4-5 liters of water daily in Skardu/Deosai.")
            print("  2. Landslide Precaution: Monitor weather alerts on Neelum Valley Road and KKH.")
            print("  3. Security Verification: Carry original CNIC/Passport for AJK & GB checkpoints.")
            print("  4. Winter Road Closures: Babusar Pass, Deosai, Ratti Gali closed Nov to May.")
            print("-" * 70)

        for idx, item in enumerate(items, 1):
            status = "[x] DONE" if item["is_completed"] == "YES" else "[ ] PENDING"
            print(f"  {idx:>2}. {status} | {item['item_title']} ({item['category']})")
        print("-" * 70)
        print("1. Toggle Item Status (Mark as Done / Pending)")
        print("2. Add Custom Packing Item")
        print("0. Back to Trips List")
        print("-" * 70)

        ch = input("Select option: ").strip()
        if ch == "1":
            try:
                i_sel = int(input("Enter Item Number to Toggle: ").strip()) - 1
                if 0 <= i_sel < len(items):
                    target = items[i_sel]
                    new_state = "NO" if target["is_completed"] == "YES" else "YES"
                    upd_sql = "UPDATE TRIP_CHECKLIST SET IS_COMPLETED = :st WHERE CHECKLIST_ID = :cid"
                    execute_non_query(upd_sql, {"st": new_state, "cid": target["checklist_id"]})
                else:
                    print("[ERROR]: Invalid item number.")
            except ValueError:
                print("[ERROR]: Invalid input.")
        elif ch == "2":
            title = input("Enter New Item Name: ").strip()
            cat = input("Category (Documents / Health / Clothing / Gear / Other): ").strip() or "Other"
            if title:
                ins_sql = "INSERT INTO TRIP_CHECKLIST (TRIP_ID, ITEM_TITLE, CATEGORY, IS_COMPLETED) VALUES (:tid, :t, :c, 'NO')"
                execute_non_query(ins_sql, {"tid": trip["trip_id"], "t": title, "c": cat})
        elif ch == "0":
            break
        else:
            print("[ERROR]: Invalid selection.")
