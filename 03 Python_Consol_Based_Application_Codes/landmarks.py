"""
Pak Voyage - Landmarks & Cultural Attractions Module
Browsing, opening hours, ticket fee estimations, accessibility, and nearby attractions viewer.
"""

from database import execute_query

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_landmarks_by_destination(dest_id, category=None):
    """Retrieves landmarks for a destination, optionally filtered by category."""
    sql = "SELECT * FROM LANDMARKS WHERE DESTINATION_ID = :did"
    params = {"did": dest_id}
    if category:
        sql += " AND UPPER(CATEGORY) LIKE UPPER(:cat)"
        params["cat"] = f"%{category}%"
    sql += " ORDER BY LANDMARK_NAME ASC"
    return execute_query(sql, params)

def display_landmarks_menu(dest_id, dest_name):
    """Interactive landmarks exploration menu."""
    while True:
        print("\n" + "=" * 65)
        print(f"      {GREEN}{BOLD}LANDMARKS & ATTRACTIONS - {dest_name.upper()}{RESET}")
        print("=" * 65)
        print("1. Browse All Landmarks")
        print("2. Search Landmarks by Name or Category")
        print("3. View Free / No-Entry-Fee Attractions")
        print("0. Back to Destination Menu")
        print("-" * 65)

        choice = input("Select an option: ").strip()

        if choice == "1":
            landmarks = get_landmarks_by_destination(dest_id)
            select_and_view_landmark(landmarks)
        elif choice == "2":
            q = input("\nEnter keyword (e.g. Mosque, Museum, Lake, Fort): ").strip()
            landmarks = get_landmarks_by_destination(dest_id, category=q)
            select_and_view_landmark(landmarks)
        elif choice == "3":
            sql = "SELECT * FROM LANDMARKS WHERE DESTINATION_ID = :did AND ENTRY_FEE_ADULT_PKR = 0 ORDER BY LANDMARK_NAME"
            landmarks = execute_query(sql, {"did": dest_id})
            select_and_view_landmark(landmarks)
        elif choice == "0":
            break
        else:
            print("[ERROR]: Invalid selection.")

def select_and_view_landmark(landmarks):
    """Lists landmarks and allows inspecting individual profiles."""
    if not landmarks:
        print("\nNo landmarks found matching your criteria.")
        return

    print("\n" + "-" * 65)
    print(f"{'#':<3} | {'LANDMARK NAME':<32} | {'CATEGORY':<20} | {'ENTRY (ADULT)'}")
    print("-" * 65)
    for idx, l in enumerate(landmarks, 1):
        fee = f"PKR {l['entry_fee_adult_pkr']:,.0f}" if l['entry_fee_adult_pkr'] > 0 else "FREE ENTRY"
        print(f"{idx:<3} | {l['landmark_name'][:32]:<32} | {l['category'][:20]:<20} | {fee}")
    print("-" * 65)

    sel = input("\nEnter Landmark Number to view details (or 0 to back): ").strip()
    if sel == "0":
        return
    try:
        idx = int(sel) - 1
        if 0 <= idx < len(landmarks):
            display_landmark_profile(landmarks[idx])
        else:
            print("[ERROR]: Invalid number.")
    except ValueError:
        print("[ERROR]: Invalid input.")

def display_landmark_profile(landmark):
    """Displays comprehensive landmark information and ticket calculator."""
    print("\n" + "=" * 65)
    print(f"      {landmark['landmark_name'].upper()}")
    print("=" * 65)
    print(f"Category:             {landmark['category']}")
    print(f"Location:             {landmark['location_address']}")
    print(f"Opening Schedule:     {landmark.get('opening_days') or 'All Days'} ({landmark.get('opening_hours') or 'Open'})")
    print(f"Est. Visit Duration:  {landmark.get('est_duration_hours') or '1.5'} Hours")
    print(f"Adult Ticket:         PKR {landmark['entry_fee_adult_pkr']:,.2f}")
    print(f"Child Ticket:         PKR {landmark['entry_fee_child_pkr']:,.2f}")
    print(f"Accessibility:        {landmark.get('accessibility_info') or 'Standard access'}")
    print(f"Nearby Attractions:   {landmark.get('nearby_attractions') or 'None recorded'}")
    print(f"Source Authority:     {landmark.get('source_url') or 'Official Department'}")
    print(f"Last Verification:    {landmark.get('last_verified_date') or 'Verified'}")
    print("-" * 65)
    print(f"Description:\n  {landmark['description']}")
    print("-" * 65)

    # Ticket cost calculator
    if landmark['entry_fee_adult_pkr'] > 0 or landmark['entry_fee_child_pkr'] > 0:
        calc_opt = input("\nCalculate visitor ticket cost for your group? (y/n): ").strip().lower()
        if calc_opt == "y":
            try:
                adults = int(input("Number of Adults: ").strip())
                children = int(input("Number of Children: ").strip())
                total = (adults * landmark['entry_fee_adult_pkr']) + (children * landmark['entry_fee_child_pkr'])
                print(f"\nEstimated Ticket Cost for {adults} Adult(s) + {children} Child(ren): PKR {total:,.2f}")
            except ValueError:
                print("[ERROR]: Please enter valid numbers.")
    input("\nPress Enter to continue...")
