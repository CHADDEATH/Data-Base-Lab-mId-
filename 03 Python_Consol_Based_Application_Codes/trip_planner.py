"""
Pak Voyage - Multi-Destination Trip Planner Module
Supports creating multi-city itineraries, day-wise scheduling, seasonal warnings, and printable summaries.
"""

import os
from database import execute_query, execute_non_query, execute_insert_returning_id
from destinations import get_all_destinations

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "05_Reports")

def get_user_trips(user_id):
    """Retrieves all trips planned by a tourist."""
    sql = "SELECT * FROM TRIPS WHERE USER_ID = :uid ORDER BY START_DATE DESC"
    return execute_query(sql, {"uid": user_id})

def get_trip_destinations(trip_id):
    """Retrieves destinations attached to a trip in visit order."""
    sql = """
        SELECT td.*, d.DESTINATION_NAME, d.PROVINCE_REGION, d.BEST_TIME_TO_VISIT
        FROM TRIP_DESTINATIONS td
        JOIN DESTINATIONS d ON td.DESTINATION_ID = d.DESTINATION_ID
        WHERE td.TRIP_ID = :tid
        ORDER BY td.VISIT_ORDER ASC
    """
    return execute_query(sql, {"tid": trip_id})

def get_trip_itinerary(trip_id):
    """Retrieves day-by-day scheduled itinerary items."""
    sql = """
        SELECT ti.*, d.DESTINATION_NAME
        FROM TRIP_ITINERARY ti
        JOIN DESTINATIONS d ON ti.DESTINATION_ID = d.DESTINATION_ID
        WHERE ti.TRIP_ID = :tid
        ORDER BY ti.DAY_NUMBER ASC, 
            CASE ti.TIME_SLOT 
                WHEN 'Morning' THEN 1 
                WHEN 'Afternoon' THEN 2 
                WHEN 'Evening' THEN 3 
                WHEN 'Night' THEN 4 
                ELSE 5 
            END
    """
    return execute_query(sql, {"tid": trip_id})

def create_new_trip(current_user):
    """Guides user through creating a new multi-destination trip plan."""
    print("\n" + "=" * 65)
    print(f"      {GREEN}{BOLD}CREATE NEW MULTI-DESTINATION TRIP PLAN{RESET}")
    print("=" * 65)
    name = input("Trip Name (e.g. Northern Pakistan Expedition 2026): ").strip()
    if not name:
        print("[ERROR]: Trip name is required.")
        return

    start_date = input("Start Date (YYYY-MM-DD): ").strip()
    end_date = input("End Date (YYYY-MM-DD): ").strip()

    try:
        travellers = int(input("Total Number of Travellers: ").strip())
        adults = int(input("Number of Adults: ").strip())
        children = int(input("Number of Children: ").strip())
        budget = float(input("Total Target Budget in PKR (e.g. 250000): ").strip())
    except ValueError:
        print("[ERROR]: Invalid numeric values.")
        return

    prefs = input("Travel Preferences (e.g. Nature, Hiking, Historical): ").strip()
    desc = input("Trip Description / Objectives: ").strip()

    # Insert into TRIPS table
    sql = """
        INSERT INTO TRIPS (
            USER_ID, TRIP_NAME, START_DATE, END_DATE, 
            NUM_TRAVELLERS, NUM_ADULTS, NUM_CHILDREN, BUDGET_PKR, 
            TRAVEL_PREFERENCES, TRIP_DESCRIPTION, CREATED_AT, STATUS
        ) VALUES (
            :uid, :name, TO_DATE(:sdate, 'YYYY-MM-DD'), TO_DATE(:edate, 'YYYY-MM-DD'),
            :trav, :ad, :ch, :bgt, :prefs, :desc, SYSDATE, 'PLANNED'
        ) RETURNING TRIP_ID INTO :out_id
    """
    params = {
        "uid": current_user["user_id"],
        "name": name,
        "sdate": start_date,
        "edate": end_date,
        "trav": travellers,
        "ad": adults,
        "ch": children,
        "bgt": budget,
        "prefs": prefs,
        "desc": desc
    }

    trip_id, err = execute_insert_returning_id(sql, params)
    if err:
        print(f"[ERROR]: Failed to create trip: {err}")
        return

    # Add default checklist items
    from checklist import populate_default_checklist
    populate_default_checklist(trip_id)

    print(f"\n[SUCCESS]: Trip '{name}' created successfully with Trip ID #{trip_id}.")

    # Add destinations flow
    manage_trip_destinations(trip_id)

def manage_trip_destinations(trip_id):
    """Allows adding and ordering destinations in a trip."""
    all_dests = get_all_destinations()
    print("\n" + "-" * 65)
    print("      ADD DESTINATIONS TO YOUR JOURNEY")
    print("-" * 65)
    for idx, d in enumerate(all_dests, 1):
        print(f"  {idx}. {d['destination_name']} ({d['province_region']})")

    print("\nEnter destination numbers in order of visit (comma separated, e.g. 1, 4, 5):")
    order_input = input("Destinations: ").strip()
    if not order_input:
        return

    order_seq = 1
    for part in order_input.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(all_dests):
                dest = all_dests[idx]
                try:
                    days = int(input(f"Estimated days to stay in {dest['destination_name']}: ").strip() or "2")
                except ValueError:
                    days = 2

                ins_sql = """
                    INSERT INTO TRIP_DESTINATIONS (TRIP_ID, DESTINATION_ID, VISIT_ORDER, STAY_DAYS)
                    VALUES (:tid, :did, :vord, :days)
                """
                execute_non_query(ins_sql, {
                    "tid": trip_id,
                    "did": dest["destination_id"],
                    "vord": order_seq,
                    "days": days
                })
                print(f"  -> Added {dest['destination_name']} as Stop #{order_seq} ({days} days)")
                order_seq += 1

def display_my_trips_menu(current_user):
    """Interactive management for tourist's trips."""
    while True:
        trips = get_user_trips(current_user["user_id"])
        print("\n" + "=" * 70)
        print(f"      {GREEN}{BOLD}MY TRIPS & VACATION PLANS - {current_user['full_name'].upper()}{RESET}")
        print("=" * 70)

        if not trips:
            print("You have not created any trips yet.")
            print("\n1. Plan a New Trip")
            print("0. Back to Dashboard")
            ch = input("\nSelect: ").strip()
            if ch == "1":
                create_new_trip(current_user)
            elif ch == "0":
                break
            continue

        print(f"{'#':<3} | {'TRIP NAME':<28} | {'DATES':<22} | {'BUDGET':<12} | {'STATUS'}")
        print("-" * 70)
        for idx, t in enumerate(trips, 1):
            sdate = str(t.get('start_date') or '').split()[0]
            edate = str(t.get('end_date') or '').split()[0]
            dates_str = f"{sdate} to {edate}"
            print(f"{idx:<3} | {t['trip_name'][:28]:<28} | {dates_str:<22} | PKR {t['budget_pkr']:<8,.0f} | {t['status']}")
        print("-" * 70)
        print("1. View / Edit Trip Itinerary & Schedule")
        print("2. Add Activities / Stops to Itinerary")
        print("3. Generate Printable Trip Summary Report")
        print("4. Plan a New Trip")
        print("0. Back to Dashboard")

        choice = input("\nSelect option: ").strip()
        if choice == "1":
            trip = select_trip(trips)
            if trip:
                display_full_trip_itinerary(trip)
        elif choice == "2":
            trip = select_trip(trips)
            if trip:
                add_itinerary_item(trip)
        elif choice == "3":
            trip = select_trip(trips)
            if trip:
                export_printable_summary(trip, current_user)
        elif choice == "4":
            create_new_trip(current_user)
        elif choice == "0":
            break
        else:
            print("[ERROR]: Invalid selection.")

def select_trip(trips):
    """Helper to pick a trip from the list."""
    try:
        t_sel = int(input("\nEnter Trip Number: ").strip()) - 1
        if 0 <= t_sel < len(trips):
            return trips[t_sel]
        print("[ERROR]: Invalid number.")
    except ValueError:
        print("[ERROR]: Invalid input.")
    return None

def display_full_trip_itinerary(trip):
    """Displays complete day-by-day itinerary with seasonal weather alerts."""
    print("\n" + "=" * 70)
    print(f"      ITINERARY: {trip['trip_name'].upper()}")
    print("=" * 70)
    sdate = str(trip.get('start_date') or '').split()[0]
    edate = str(trip.get('end_date') or '').split()[0]
    print(f"Schedule:            {sdate} to {edate} | Travellers: {trip['num_travellers']} ({trip['num_adults']} Adults, {trip['num_children']} Children)")
    print(f"Allocated Budget:    PKR {trip['budget_pkr']:,.2f}")
    print(f"Preferences:         {trip.get('travel_preferences') or 'General exploration'}")
    print("-" * 70)

    # Destinations in this trip
    dest_stops = get_trip_destinations(trip["trip_id"])
    print("Destinations on Journey:")
    for d in dest_stops:
        print(f"  Stop #{d['visit_order']}: {d['destination_name']} ({d['stay_days']} days) [Best: {d['best_time_to_visit']}]")

    # Day-wise items
    items = get_trip_itinerary(trip["trip_id"])
    print("\nDAY-WISE SCHEDULE:")
    print("-" * 70)
    if not items:
        print("No specific activities scheduled yet. Use option 'Add Activities to Itinerary'.")
    else:
        current_day = None
        for it in items:
            if it["day_number"] != current_day:
                current_day = it["day_number"]
                print(f"\nDAY {current_day} - {it['destination_name'].upper()}")
            cost_str = f" [Est. PKR {it['est_cost_pkr']:,.0f}]" if it['est_cost_pkr'] > 0 else ""
            print(f"  - [{it['time_slot']}] {it['item_title']} ({it['item_type']}){cost_str}")
            if it.get('notes'):
                print(f"      Notes: {it['notes']}")
    print("=" * 70)
    input("\nPress Enter to continue...")

def add_itinerary_item(trip):
    """Allows adding an activity, landmark, trail, or custom stop to a specific day."""
    dest_stops = get_trip_destinations(trip["trip_id"])
    if not dest_stops:
        print("\nPlease add at least one destination to this trip first.")
        return

    print("\nSelect Destination for this scheduled activity:")
    for idx, d in enumerate(dest_stops, 1):
        print(f"  {idx}. {d['destination_name']}")

    try:
        d_sel = int(input("Destination: ").strip()) - 1
        if not (0 <= d_sel < len(dest_stops)):
            print("[ERROR]: Invalid selection.")
            return
        dest = dest_stops[d_sel]

        day_num = int(input(f"Day Number (1, 2, 3...): ").strip())
        print("Time Slot: 1. Morning | 2. Afternoon | 3. Evening | 4. Night | 5. Full Day")
        slot_map = {"1": "Morning", "2": "Afternoon", "3": "Evening", "4": "Night", "5": "Full Day"}
        slot = slot_map.get(input("Slot (1-5): ").strip(), "Morning")

        print("Item Category: 1. HOTEL | 2. LANDMARK | 3. TRAIL | 4. ACTIVITY | 5. RESTAURANT | 6. TRANSPORT | 7. CUSTOM")
        cat_map = {"1": "HOTEL", "2": "LANDMARK", "3": "TRAIL", "4": "ACTIVITY", "5": "RESTAURANT", "6": "TRANSPORT", "7": "CUSTOM"}
        item_type = cat_map.get(input("Category (1-7): ").strip(), "CUSTOM")

        title = input("Activity Title / Description: ").strip()
        cost = float(input("Estimated Cost in PKR (or 0): ").strip() or "0")
        notes = input("Additional Notes: ").strip()

        sql = """
            INSERT INTO TRIP_ITINERARY (
                TRIP_ID, DESTINATION_ID, DAY_NUMBER, TIME_SLOT, 
                ITEM_TYPE, ITEM_TITLE, EST_COST_PKR, NOTES
            ) VALUES (
                :tid, :did, :day, :slot, :type, :title, :cost, :notes
            )
        """
        ok, _, err = execute_non_query(sql, {
            "tid": trip["trip_id"],
            "did": dest["destination_id"],
            "day": day_num,
            "slot": slot,
            "type": item_type,
            "title": title,
            "cost": cost,
            "notes": notes
        })
        if ok:
            print(f"\n[SUCCESS]: Scheduled '{title}' for Day {day_num} ({slot}).")
        else:
            print(f"[ERROR]: {err}")
        input("Press Enter to continue...")
    except ValueError:
        print("[ERROR]: Invalid input.")

def export_printable_summary(trip, current_user):
    """Generates a clean, formatted ASCII text itinerary and expense voucher file."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filename = f"Trip_Summary_Trip_{trip['trip_id']}.txt"
    filepath = os.path.join(REPORTS_DIR, filename)

    dest_stops = get_trip_destinations(trip["trip_id"])
    itinerary_items = get_trip_itinerary(trip["trip_id"])

    # Gather bookings
    bkg_sql = "SELECT * FROM BOOKINGS WHERE TRIP_ID = :tid ORDER BY BOOKING_DATE"
    bookings = execute_query(bkg_sql, {"tid": trip["trip_id"]})

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("                 PAK VOYAGE TRAVEL MANAGEMENT\n")
        f.write("             OFFICIAL COMPREHENSIVE TRIP SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Trip Name:          {trip['trip_name']}\n")
        f.write(f"Customer Name:      {current_user['full_name']} ({current_user['email']})\n")
        f.write(f"Travel Window:      {str(trip.get('start_date') or '').split()[0]} to {str(trip.get('end_date') or '').split()[0]}\n")
        f.write(f"Travellers:         {trip['num_travellers']} Total ({trip['num_adults']} Adults, {trip['num_children']} Children)\n")
        f.write(f"Allocated Budget:   PKR {trip['budget_pkr']:,.2f}\n")
        f.write(f"Preferences:        {trip.get('travel_preferences') or 'General Leisure'}\n\n")
        
        f.write("-" * 70 + "\n")
        f.write("DESTINATIONS & STAYS:\n")
        f.write("-" * 70 + "\n")
        for d in dest_stops:
            f.write(f"- Stop #{d['visit_order']}: {d['destination_name']} ({d['province_region']}) - {d['stay_days']} Days [Best Season: {d['best_time_to_visit']}]\n")

        f.write("\n" + "-" * 70 + "\n")
        f.write("DAY-WISE ITINERARY:\n")
        f.write("-" * 70 + "\n")
        current_day = None
        for it in itinerary_items:
            if it["day_number"] != current_day:
                current_day = it["day_number"]
                f.write(f"\nDAY {current_day} - {it['destination_name'].upper()}:\n")
            cost_str = f" [Est. PKR {it['est_cost_pkr']:,.2f}]" if it['est_cost_pkr'] > 0 else ""
            f.write(f"  * [{it['time_slot']}] {it['item_title']} ({it['item_type']}){cost_str}\n")
            if it.get('notes'):
                f.write(f"    Notes: {it['notes']}\n")

        f.write("\n" + "-" * 70 + "\n")
        f.write("CONFIRMED APPLICATION BOOKINGS:\n")
        f.write("-" * 70 + "\n")
        total_bkg_cost = 0.0
        if bookings:
            for b in bookings:
                f.write(f"- Ref: {b['booking_ref']} | Type: {b['service_type']} | Date: {str(b.get('travel_date') or '').split()[0]} | Total: PKR {b['total_cost_pkr']:,.2f} | Status: {b['booking_status']}\n")
                if b['booking_status'] != 'Cancelled':
                    total_bkg_cost += b['total_cost_pkr']
        else:
            f.write("No bookings currently linked to this trip.\n")

        f.write(f"\nTotal Confirmed Bookings Value: PKR {total_bkg_cost:,.2f}\n")
        f.write(f"Remaining Available Budget:     PKR {(trip['budget_pkr'] - total_bkg_cost):,.2f}\n")
        f.write("=" * 70 + "\n")
        f.write("Generated dynamically by Pak Voyage Travel Management System.\n")
        f.write("=" * 70 + "\n")

    print(f"\n[SUCCESS]: Printable trip summary exported successfully to:")
    print(f"  {filepath}")
    input("\nPress Enter to continue...")
