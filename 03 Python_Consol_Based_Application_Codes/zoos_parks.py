"""
Pak Voyage - Zoos, Wildlife Parks & Family Attractions Module
Covers Zoos, Safari Parks, Bird Aviaries, Nature Reserves, and Sub-Attraction Tickets.
Includes Multi-Tier Family Ticket Cost Calculator.
"""

from database import execute_query

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_facilities_by_destination(dest_id):
    """Retrieves zoos and wildlife parks for a destination."""
    sql = "SELECT * FROM ZOOS_PARKS WHERE DESTINATION_ID = :did ORDER BY FACILITY_NAME ASC"
    return execute_query(sql, {"did": dest_id})

def get_sub_tickets(facility_id):
    """Retrieves sub-attraction ticket options for a facility."""
    sql = "SELECT * FROM FACILITY_TICKETS WHERE FACILITY_ID = :fid ORDER BY TICKET_PRICE_PKR ASC"
    return execute_query(sql, {"fid": facility_id})

def display_zoos_menu(dest_id, dest_name):
    """Interactive zoos and family parks menu."""
    while True:
        print("\n" + "=" * 65)
        print(f"      {GREEN}{BOLD}ZOOS, WILDLIFE PARKS & FAMILY ATTRACTIONS - {dest_name.upper()}{RESET}")
        print("=" * 65)
        print("1. Browse All Wildlife & Family Facilities")
        print("2. Family Cost Estimator (Adults, Children, Special Exhibits, Parking)")
        print("0. Back to Destination Menu")
        print("-" * 65)

        choice = input("Select an option: ").strip()

        if choice == "1":
            facs = get_facilities_by_destination(dest_id)
            select_and_view_facility(facs)
        elif choice == "2":
            facs = get_facilities_by_destination(dest_id)
            family_cost_calculator(facs)
        elif choice == "0":
            break
        else:
            print("[ERROR]: Invalid selection.")

def select_and_view_facility(facilities):
    """Lists facilities and allows viewing details."""
    if not facilities:
        print("\nNo facilities recorded for this destination.")
        return

    print("\n" + "-" * 70)
    print(f"{'#':<3} | {'FACILITY NAME':<32} | {'TYPE':<20} | {'ADULT TICKET'}")
    print("-" * 70)
    for idx, f in enumerate(facilities, 1):
        fee = f"PKR {f['adult_ticket_pkr']:,.0f}" if f['adult_ticket_pkr'] > 0 else "FREE ENTRY"
        print(f"{idx:<3} | {f['facility_name'][:32]:<32} | {f['facility_type'][:20]:<20} | {fee}")
    print("-" * 70)

    sel = input("\nEnter Facility Number to inspect (or 0 to back): ").strip()
    if sel == "0":
        return
    try:
        idx = int(sel) - 1
        if 0 <= idx < len(facilities):
            display_facility_profile(facilities[idx])
        else:
            print("[ERROR]: Invalid number.")
    except ValueError:
        print("[ERROR]: Invalid input.")

def display_facility_profile(fac):
    """Displays full ticket schedule and sub-attraction passes."""
    print("\n" + "=" * 65)
    print(f"      {fac['facility_name'].upper()}")
    print("=" * 65)
    print(f"Type:                 {fac['facility_type']}")
    print(f"Address:              {fac['address']}")
    print(f"Opening Hours:        {fac.get('opening_hours') or '09:00 - Sunset'} (Weekly Off: {fac.get('weekly_off') or 'None'})")
    print(f"Adult Ticket:         PKR {fac['adult_ticket_pkr']:,.2f}")
    print(f"Child Ticket:         PKR {fac['child_ticket_pkr']:,.2f}")
    print(f"Student Ticket:       PKR {fac['student_ticket_pkr']:,.2f}")
    if fac.get('family_package_pkr') and fac['family_package_pkr'] > 0:
        print(f"Family Package:       PKR {fac['family_package_pkr']:,.2f} (2 Adults + 2 Children)")
    print(f"Vehicle Parking:      PKR {fac['parking_fee_pkr']:,.2f}")
    print(f"Contact Phone:        {fac.get('contact_phone') or 'Department Line'}")
    print(f"Official Source:      {fac.get('source_url') or 'Wildlife Department'}")
    print("-" * 65)
    print(f"Description:\n  {fac['description']}")
    print("-" * 65)

    sub_tkts = get_sub_tickets(fac["facility_id"])
    if sub_tkts:
        print("\nSpecialized Exhibits & Sub-Attractions inside Facility:")
        for st in sub_tkts:
            print(f"  - {st['attraction_name']}: PKR {st['ticket_price_pkr']:,.2f} ({st.get('description') or ''})")
    input("\nPress Enter to continue...")

def family_cost_calculator(facilities):
    """Calculates comprehensive family day-out cost."""
    if not facilities:
        print("\nNo facilities available.")
        return

    print("\nSelect Facility to calculate family visit cost:")
    for idx, f in enumerate(facilities, 1):
        print(f"  {idx}. {f['facility_name']} ({f['facility_type']})")

    try:
        f_sel = int(input("\nFacility Number: ").strip())
        if f_sel < 1 or f_sel > len(facilities):
            print("[ERROR]: Invalid selection.")
            return

        fac = facilities[f_sel - 1]
        adults = int(input("Number of Adults: ").strip())
        children = int(input("Number of Children: ").strip())
        vehicles = int(input("Number of Cars/Vehicles for Parking: ").strip())

        base_tickets = (adults * fac["adult_ticket_pkr"]) + (children * fac["child_ticket_pkr"])
        parking_total = vehicles * fac["parking_fee_pkr"]

        sub_tkts = get_sub_tickets(fac["facility_id"])
        sub_total = 0.0
        if sub_tkts:
            print("\nAvailable Special Exhibits / Rides:")
            for s_idx, st in enumerate(sub_tkts, 1):
                inc = input(f"Include {st['attraction_name']} (PKR {st['ticket_price_pkr']:,.0f} per person)? (y/n): ").strip().lower()
                if inc == "y":
                    sub_total += st["ticket_price_pkr"] * (adults + children)

        grand_total = base_tickets + parking_total + sub_total

        print("\n" + "=" * 65)
        print("          FAMILY ATTRACTION EXPENSE BREAKDOWN")
        print("=" * 65)
        print(f"Facility:               {fac['facility_name']}")
        print(f"Visitors:               {adults} Adult(s), {children} Child(ren)")
        print(f"General Admission:      PKR {base_tickets:,.2f}")
        print(f"Special Exhibits/Rides: PKR {sub_total:,.2f}")
        print(f"Parking Charges:        PKR {parking_total:,.2f}")
        print("-" * 65)
        print(f"TOTAL ESTIMATED COST:   PKR {grand_total:,.2f}")
        print("=" * 65)
        input("\nPress Enter to continue...")
    except ValueError:
        print("[ERROR]: Invalid numeric input.")
