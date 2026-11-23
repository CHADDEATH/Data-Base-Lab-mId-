"""
Pak Voyage - Fun, Adventure & Recreation Activities Module
Covers Boating, Paragliding, Ziplining, Desert Safaris, Camping, Scuba Diving, and Family Activities.
Supports multiple pricing models and activity booking.
"""

from database import execute_query
from booking import create_booking_record

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_activities_by_destination(dest_id, category=None):
    """Retrieves activities for a destination, optionally filtered by category."""
    sql = "SELECT * FROM ACTIVITIES WHERE DESTINATION_ID = :did"
    params = {"did": dest_id}
    if category:
        sql += " AND UPPER(CATEGORY) = UPPER(:cat)"
        params["cat"] = category
    sql += " ORDER BY PRICE_PKR ASC"
    return execute_query(sql, params)

def display_activities_menu(dest_id, dest_name, current_user=None, current_trip_id=None):
    """Interactive adventure activities menu."""
    while True:
        print("\n" + "=" * 65)
        print(f"      {GREEN}{BOLD}FUN & ADVENTURE ACTIVITIES - {dest_name.upper()}{RESET}")
        print("=" * 65)
        print("1. Browse All Activities")
        print("2. Filter by Category (Boating, Paragliding, Jeep Safari, Camping, etc.)")
        print("3. Compare Two Activities")
        print("0. Back to Destination Menu")
        print("-" * 65)

        choice = input("Select an option: ").strip()

        if choice == "1":
            acts = get_activities_by_destination(dest_id)
            select_and_view_activity(acts, dest_name, current_user, current_trip_id)
        elif choice == "2":
            cat = input("\nEnter category (e.g. Boating, Paragliding, Jeep Safari, Camping, Motorsports): ").strip()
            acts = get_activities_by_destination(dest_id, category=cat)
            select_and_view_activity(acts, dest_name, current_user, current_trip_id)
        elif choice == "3":
            compare_activities(dest_id)
        elif choice == "0":
            break
        else:
            print("[ERROR]: Invalid selection.")

def select_and_view_activity(activities, dest_name, current_user, current_trip_id):
    """Lists activities and allows inspecting and booking."""
    if not activities:
        print(f"\nNo activities found matching criteria in {dest_name}.")
        return

    print("\n" + "-" * 70)
    print(f"{'#':<3} | {'ACTIVITY NAME':<28} | {'CATEGORY':<16} | {'PRICE':<14} | {'MODEL'}")
    print("-" * 70)
    for idx, a in enumerate(activities, 1):
        print(f"{idx:<3} | {a['activity_name'][:28]:<28} | {a['category'][:16]:<16} | PKR {a['price_pkr']:<10,.0f} | {a['pricing_model']}")
    print("-" * 70)

    sel = input("\nEnter Activity Number to inspect or book (or 0 to back): ").strip()
    if sel == "0":
        return
    try:
        idx = int(sel) - 1
        if 0 <= idx < len(activities):
            display_activity_profile(activities[idx], current_user, current_trip_id)
        else:
            print("[ERROR]: Invalid number.")
    except ValueError:
        print("[ERROR]: Invalid input.")

def display_activity_profile(activity, current_user, current_trip_id):
    """Displays full activity details and interactive booking calculator."""
    print("\n" + "=" * 65)
    print(f"      {activity['activity_name'].upper()}")
    print("=" * 65)
    print(f"Category:             {activity['category']}")
    print(f"Location:             {activity['location_address']}")
    print(f"Operator:             {activity.get('operator_name') or 'Certified Tour Operator'}")
    print(f"Price:                PKR {activity['price_pkr']:,.2f} ({activity['pricing_model']})")
    print(f"Duration:             {activity.get('duration_text') or 'Variable'}")
    print(f"Operating Season:     {activity.get('operating_season') or 'All Year'}")
    print(f"Opening Hours:        {activity.get('opening_hours') or 'Open'}")
    print(f"Min Age:              {activity.get('min_age') or 0} Years")
    print(f"Max Participants:     {activity.get('max_participants') or 'Open'}")
    print(f"Safety Requirements:  {activity.get('safety_requirements') or 'Standard safety briefing provided'}")
    print(f"Verification:         {activity.get('last_verified_date') or 'Verified'}")
    print("-" * 65)
    print(f"Description:\n  {activity['description']}")
    print("-" * 65)

    if not current_user:
        print("\n[NOTE]: Sign in as a tourist to book this activity.")
        input("Press Enter to continue...")
        return

    book_opt = input("\nWould you like to book this activity? (y/n): ").strip().lower()
    if book_opt != "y":
        return

    try:
        travel_date = input("Enter Planned Date (YYYY-MM-DD): ").strip()
        model = activity["pricing_model"]
        qty = 1
        total_cost = activity["price_pkr"]

        if "Person" in model or "Ride" in model or "Flight" in model:
            qty = int(input(f"Enter quantity ({model}): ").strip())
            total_cost = activity["price_pkr"] * qty
        elif "Hour" in model:
            qty = int(input("Enter number of hours: ").strip())
            total_cost = activity["price_pkr"] * qty
        elif "Night" in model:
            qty = int(input("Enter number of nights: ").strip())
            total_cost = activity["price_pkr"] * qty

        print(f"\nCalculated Total Cost: PKR {total_cost:,.2f}")
        confirm = input("Confirm booking record in Oracle? (y/n): ").strip().lower()
        if confirm == "y":
            notes = f"Activity: {activity['activity_name']} ({model}), Qty: {qty}"
            ok, bkg_ref, msg = create_booking_record(
                user_id=current_user["user_id"],
                trip_id=current_trip_id,
                service_type="ACTIVITY",
                service_ref_id=activity["activity_id"],
                travel_date=travel_date,
                quantity=qty,
                unit_price_pkr=activity["price_pkr"],
                total_cost_pkr=total_cost,
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

def compare_activities(dest_id):
    """Compares two activities side-by-side."""
    acts = get_activities_by_destination(dest_id)
    if len(acts) < 2:
        print("\nNot enough activities for comparison.")
        return

    print("\nSelect Two Activities to Compare:")
    for idx, a in enumerate(acts, 1):
        print(f"  {idx}. {a['activity_name']} ({a['category']} - PKR {a['price_pkr']:,.0f})")

    try:
        a1 = int(input("\nFirst Activity: ").strip())
        a2 = int(input("Second Activity: ").strip())
        if a1 < 1 or a1 > len(acts) or a2 < 1 or a2 > len(acts) or a1 == a2:
            print("[ERROR]: Invalid selection.")
            return

        act1 = acts[a1 - 1]
        act2 = acts[a2 - 1]

        p1_str = f"PKR {act1['price_pkr']:,.0f}"
        p2_str = f"PKR {act2['price_pkr']:,.0f}"
        age1_str = f"{act1['min_age']} years"
        age2_str = f"{act2['min_age']} years"

        print("\n" + "=" * 70)
        print(f"{'CRITERIA':<25} | {act1['activity_name'][:20]:<20} | {act2['activity_name'][:20]:<20}")
        print("=" * 70)
        print(f"{'Category':<25} | {act1['category']:<20} | {act2['category']:<20}")
        print(f"{'Price (PKR)':<25} | {p1_str:<20} | {p2_str:<20}")
        print(f"{'Pricing Model':<25} | {act1['pricing_model']:<20} | {act2['pricing_model']:<20}")
        print(f"{'Duration':<25} | {act1.get('duration_text') or 'N/A':<20} | {act2.get('duration_text') or 'N/A':<20}")
        print(f"{'Min Age':<25} | {age1_str:<20} | {age2_str:<20}")
        print(f"{'Operating Season':<25} | {act1.get('operating_season') or 'All Year':<20} | {act2.get('operating_season') or 'All Year':<20}")
        print("=" * 70)
        input("\nPress Enter to continue...")
    except ValueError:
        print("[ERROR]: Invalid input.")
