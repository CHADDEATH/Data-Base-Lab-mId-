"""
Pak Voyage - Dedicated Trails, Hiking & Trekking Management Module
Supports Islamabad Trails, Skardu Mountain Expeditions, and Kashmir Lake Treks.
Includes difficulty filters, guide/porter requirements, and individual/group cost calculators.
"""

from database import execute_query
from booking import create_booking_record

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_trails_by_destination(dest_id, difficulty=None):
    """Retrieves trails for a destination, optionally filtered by difficulty."""
    sql = "SELECT * FROM TRAILS WHERE DESTINATION_ID = :did"
    params = {"did": dest_id}
    if difficulty:
        sql += " AND UPPER(DIFFICULTY_LEVEL) = UPPER(:diff)"
        params["diff"] = difficulty
    sql += " ORDER BY DISTANCE_KM ASC"
    return execute_query(sql, params)

def get_trail_services(trail_id):
    """Retrieves available add-on services for a trail."""
    sql = "SELECT * FROM TRAIL_SERVICES WHERE TRAIL_ID = :tid ORDER BY IS_MANDATORY DESC, COST_PKR ASC"
    return execute_query(sql, {"tid": trail_id})

def display_trails_menu(dest_id, dest_name, current_user=None, current_trip_id=None):
    """Interactive trails and trekking menu."""
    while True:
        print("\n" + "=" * 65)
        print(f"      {GREEN}{BOLD}TRAILS, HIKING & TREKKING - {dest_name.upper()}{RESET}")
        print("=" * 65)
        print("1. View All Hiking & Trekking Routes")
        print("2. Filter by Difficulty (Easy, Moderate, Difficult, Extreme)")
        print("3. View High-Altitude Expeditions (> 3,000m)")
        print("0. Back to Destination Menu")
        print("-" * 65)

        choice = input("Select an option: ").strip()

        if choice == "1":
            trails = get_trails_by_destination(dest_id)
            select_and_view_trail(trails, dest_name, current_user, current_trip_id)
        elif choice == "2":
            print("\nSelect Difficulty Level:")
            print("1. Easy (Family friendly, gentle incline)")
            print("2. Moderate (Active hikers, some steep ascents)")
            print("3. Difficult (Strenuous, high stamina required)")
            print("4. Extreme (Wilderness expeditions, technical mountaineering)")
            d_sel = input("Enter choice (1-4): ").strip()
            diff_map = {"1": "Easy", "2": "Moderate", "3": "Difficult", "4": "Extreme"}
            diff = diff_map.get(d_sel)
            if diff:
                trails = get_trails_by_destination(dest_id, difficulty=diff)
                select_and_view_trail(trails, dest_name, current_user, current_trip_id)
            else:
                print("[ERROR]: Invalid selection.")
        elif choice == "3":
            sql = "SELECT * FROM TRAILS WHERE DESTINATION_ID = :did AND MAX_ALTITUDE_M >= 3000 ORDER BY MAX_ALTITUDE_M DESC"
            trails = execute_query(sql, {"did": dest_id})
            select_and_view_trail(trails, dest_name, current_user, current_trip_id)
        elif choice == "0":
            break
        else:
            print("[ERROR]: Invalid selection.")

def select_and_view_trail(trails, dest_name, current_user, current_trip_id):
    """Lists trails and allows inspecting detailed route specifications."""
    if not trails:
        print(f"\nNo trails found matching criteria in {dest_name}.")
        return

    print("\n" + "-" * 70)
    print(f"{'#':<3} | {'TRAIL NAME':<30} | {'DIST':<8} | {'TIME':<12} | {'DIFFICULTY':<10} | {'MAX ALT'}")
    print("-" * 70)
    for idx, t in enumerate(trails, 1):
        alt = f"{t['max_altitude_m']}m" if t.get('max_altitude_m') else "N/A"
        print(f"{idx:<3} | {t['trail_name'][:30]:<30} | {t['distance_km']:>4.1f} km | {t['duration_text'][:12]:<12} | {t['difficulty_level'][:10]:<10} | {alt}")
    print("-" * 70)

    sel = input("\nEnter Trail Number to view route profile (or 0 to back): ").strip()
    if sel == "0":
        return
    try:
        idx = int(sel) - 1
        if 0 <= idx < len(trails):
            display_trail_profile(trails[idx], current_user, current_trip_id)
        else:
            print("[ERROR]: Invalid number.")
    except ValueError:
        print("[ERROR]: Invalid input.")

def display_trail_profile(trail, current_user, current_trip_id):
    """Displays detailed trekking route specifications, services, and cost calculator."""
    print("\n" + "=" * 65)
    print(f"      ROUTE: {trail['trail_name'].upper()} ({trail.get('trail_code') or 'N/A'})")
    print("=" * 65)
    print(f"District:             {trail['district']}")
    print(f"Starting Point:       {trail['starting_point']}")
    print(f"Ending Point:         {trail['ending_point']}")
    print(f"Distance:             {trail['distance_km']} km | Est. Duration: {trail['duration_text']}")
    print(f"Difficulty Level:     {trail['difficulty_level']}")
    if trail.get('min_altitude_m') and trail.get('max_altitude_m'):
        print(f"Altitude Range:       {trail['min_altitude_m']}m to {trail['max_altitude_m']}m")
    print(f"Recommended Season:   {trail['best_season']}")
    print(f"Guide Requirement:    {trail['guide_required']} | Porter Recommended: {trail['porter_recommended']}")
    print(f"Permit Required:      {trail['permit_required']} | Parking Available: {trail['parking_available']}")
    print(f"Base Entry Fee:       PKR {trail['base_entry_fee_pkr']:,.2f}")
    print(f"Safety Information:\n  {trail.get('safety_information') or 'Standard hiking safety precautions.'}")
    print(f"Official Source:      {trail.get('source_url') or 'Tourism Department'}")
    print("-" * 65)

    services = get_trail_services(trail["trail_id"])
    if services:
        print("\nAvailable Trail & Expedition Support Services:")
        print("-" * 65)
        for idx, s in enumerate(services, 1):
            mand = "[MANDATORY]" if s["is_mandatory"] == "YES" else "[OPTIONAL]"
            print(f"  [{idx}] {s['service_name']} ({s['service_type']}) - {mand}")
            print(f"      Cost: PKR {s['cost_pkr']:,.2f} ({s['unit_type']}) | {s.get('notes') or ''}")
        print("-" * 65)

    # Cost Estimation & Booking Engine
    est_opt = input("\nCalculate estimated expedition / trekking package cost? (y/n): ").strip().lower()
    if est_opt == "y":
        calculate_trail_cost(trail, services, current_user, current_trip_id)
    else:
        input("\nPress Enter to continue...")

def calculate_trail_cost(trail, services, current_user, current_trip_id):
    """Calculates individual and group costs for a trail expedition."""
    try:
        hikers = int(input("\nNumber of Participants / Hikers: ").strip())
        if hikers <= 0:
            print("[ERROR]: Number of participants must be greater than zero.")
            return

        base_total = trail["base_entry_fee_pkr"] * hikers
        selected_services_total = 0.0
        selected_services_notes = []

        if services:
            print("\nSelect Add-on Services to Include (comma separated numbers, e.g. 1, 2 or Enter for mandatory only):")
            user_svc_input = input("Service Numbers: ").strip()
            chosen_indices = set()
            if user_svc_input:
                for part in user_svc_input.split(","):
                    part = part.strip()
                    if part.isdigit():
                        idx = int(part) - 1
                        if 0 <= idx < len(services):
                            chosen_indices.add(idx)

            # Add mandatory services automatically
            for idx, s in enumerate(services):
                if s["is_mandatory"] == "YES" or idx in chosen_indices:
                    cost = s["cost_pkr"]
                    if "Person" in s["unit_type"]:
                        cost = cost * hikers
                    selected_services_total += cost
                    selected_services_notes.append(f"{s['service_name']} (PKR {cost:,.0f})")

        total_group_cost = base_total + selected_services_total
        cost_per_person = total_group_cost / hikers

        print("\n" + "=" * 65)
        print("          TREKKING / EXPEDITION COST BREAKDOWN")
        print("=" * 65)
        print(f"Trail:                 {trail['trail_name']}")
        print(f"Participants:          {hikers} person(s)")
        print(f"Base Entry / Permits:  PKR {base_total:,.2f}")
        print(f"Support Services:      PKR {selected_services_total:,.2f}")
        if selected_services_notes:
            print("  Included Services:")
            for note in selected_services_notes:
                print(f"   - {note}")
        print("-" * 65)
        print(f"TOTAL GROUP ESTIMATE:  PKR {total_group_cost:,.2f}")
        print(f"ESTIMATED PER PERSON:  PKR {cost_per_person:,.2f}")
        print("=" * 65)

        if not current_user:
            print("\n[NOTE]: Sign in as a tourist to save this as a booking.")
            input("Press Enter to continue...")
            return

        bkg = input("\nRecord this expedition package as an academic booking? (y/n): ").strip().lower()
        if bkg == "y":
            travel_date = input("Enter Planned Departure Date (YYYY-MM-DD): ").strip()
            notes = f"Trail: {trail['trail_name']}, Hikers: {hikers}, Services: {', '.join(selected_services_notes)}"
            ok, bkg_ref, msg = create_booking_record(
                user_id=current_user["user_id"],
                trip_id=current_trip_id,
                service_type="TREKKING",
                service_ref_id=trail["trail_id"],
                travel_date=travel_date,
                quantity=hikers,
                unit_price_pkr=cost_per_person,
                total_cost_pkr=total_group_cost,
                notes=notes
            )
            if ok:
                print(f"\n[SUCCESS]: {msg}")
                print(f"Booking Reference: {bkg_ref}")
            else:
                print(f"\n[FAILED]: {msg}")
            input("\nPress Enter to continue...")
    except ValueError:
        print("[ERROR]: Invalid numeric input.")
