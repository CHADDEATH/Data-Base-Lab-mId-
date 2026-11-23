"""
Pak Voyage - Transportation Management Module
Covers Private Vehicle Rentals (Cars, 4x4 Jeeps, Coasters) and Public Transit Routes (BRT, Metro).
Includes transparent fuel/driver pricing and vehicle booking.
"""

from database import execute_query
from booking import create_booking_record

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_transport_services(dest_id, is_public="NO"):
    """Retrieves private rentals or public services for a destination."""
    sql = """
        SELECT ts.*, tt.TYPE_NAME, tt.CATEGORY 
        FROM TRANSPORT_SERVICES ts
        JOIN TRANSPORT_TYPES tt ON ts.TRANSPORT_TYPE_ID = tt.TRANSPORT_TYPE_ID
        WHERE ts.DESTINATION_ID = :did AND ts.IS_PUBLIC = :pub
        ORDER BY ts.DAILY_RATE_PKR ASC
    """
    return execute_query(sql, {"did": dest_id, "pub": is_public})

def get_public_routes(dest_id):
    """Retrieves public transit routes for a destination."""
    sql = """
        SELECT r.*, ts.SERVICE_NAME, tt.TYPE_NAME 
        FROM PUBLIC_TRANSPORT_ROUTES r
        JOIN TRANSPORT_SERVICES ts ON r.SERVICE_ID = ts.SERVICE_ID
        JOIN TRANSPORT_TYPES tt ON ts.TRANSPORT_TYPE_ID = tt.TRANSPORT_TYPE_ID
        WHERE r.DESTINATION_ID = :did
        ORDER BY r.ROUTE_NAME ASC
    """
    return execute_query(sql, {"did": dest_id})

def get_route_stops(route_id):
    """Retrieves ordered stations/stops along a public transit route."""
    sql = "SELECT * FROM PUBLIC_TRANSPORT_STOPS WHERE ROUTE_ID = :rid ORDER BY STOP_SEQUENCE ASC"
    return execute_query(sql, {"rid": route_id})

def display_transportation_menu(dest_id, dest_name, current_user=None, current_trip_id=None):
    """Interactive transportation menu."""
    while True:
        print("\n" + "=" * 65)
        print(f"      {GREEN}{BOLD}TRANSPORTATION SERVICES - {dest_name.upper()}{RESET}")
        print("=" * 65)
        print("1. Private Vehicle Rentals (Cars, 4x4 Jeeps, HiAce, Coaster)")
        print("2. Public Transit Systems & Bus Routes (Metrobus, BRT, Orange Line)")
        print("0. Back to Destination Menu")
        print("-" * 65)

        choice = input("Select an option: ").strip()

        if choice == "1":
            services = get_transport_services(dest_id, is_public="NO")
            select_and_view_private_vehicle(services, dest_name, current_user, current_trip_id)
        elif choice == "2":
            routes = get_public_routes(dest_id)
            select_and_view_public_routes(routes, dest_name)
        elif choice == "0":
            break
        else:
            print("[ERROR]: Invalid selection.")

def select_and_view_private_vehicle(services, dest_name, current_user, current_trip_id):
    """Lists private fleet options and allows booking with transparent fuel/driver calculation."""
    if not services:
        print(f"\nNo private rental operators registered in {dest_name}.")
        return

    print("\n" + "-" * 70)
    print(f"{'#':<3} | {'SERVICE NAME':<28} | {'TYPE':<16} | {'DAILY RATE':<12} | {'CAPACITY'}")
    print("-" * 70)
    for idx, s in enumerate(services, 1):
        print(f"{idx:<3} | {s['service_name'][:28]:<28} | {s['type_name'][:16]:<16} | PKR {s['daily_rate_pkr']:<8,.0f} | {s['passenger_capacity']} seats")
    print("-" * 70)

    sel = input("\nEnter Vehicle Number to view rental policy and book (or 0 to back): ").strip()
    if sel == "0":
        return
    try:
        idx = int(sel) - 1
        if 0 <= idx < len(services):
            display_vehicle_profile(services[idx], current_user, current_trip_id)
        else:
            print("[ERROR]: Invalid number.")
    except ValueError:
        print("[ERROR]: Invalid input.")

def display_vehicle_profile(svc, current_user, current_trip_id):
    """Displays vehicle terms, fuel policies, and booking calculation."""
    print("\n" + "=" * 65)
    print(f"      {svc['service_name'].upper()}")
    print("=" * 65)
    print(f"Vehicle Type:         {svc['type_name']}")
    print(f"Operator:             {svc.get('operator_name') or 'Fleet Rental Operator'}")
    print(f"Passenger Capacity:   {svc['passenger_capacity']} Persons")
    print(f"Daily Rental Rate:    PKR {svc['daily_rate_pkr']:,.2f}")
    if svc.get('per_km_rate_pkr') and svc['per_km_rate_pkr'] > 0:
        print(f"Per-Km Surcharge:     PKR {svc['per_km_rate_pkr']:,.2f} / km")
    if svc.get('driver_charges_pkr') and svc['driver_charges_pkr'] > 0:
        print(f"Chauffeur Charges:    PKR {svc['driver_charges_pkr']:,.2f} / day")
    print(f"Fuel Policy:          {svc.get('fuel_policy') or 'Customer pays fuel'}")
    if svc.get('security_deposit_pkr') and svc['security_deposit_pkr'] > 0:
        print(f"Refundable Deposit:   PKR {svc['security_deposit_pkr']:,.2f}")
    print(f"Contact Phone:        {svc.get('contact_phone') or 'Provided on booking'}")
    print("-" * 65)

    if not current_user:
        print("\n[NOTE]: Sign in as a tourist to book private transportation.")
        input("Press Enter to continue...")
        return

    book_opt = input("\nWould you like to book this vehicle? (y/n): ").strip().lower()
    if book_opt != "y":
        return

    try:
        days = int(input("Number of Rental Days: ").strip())
        travel_date = input("Start Date (YYYY-MM-DD): ").strip()
        include_driver = input("Include Dedicated Chauffeur? (y/n): ").strip().lower() == "y"

        total = svc["daily_rate_pkr"] * days
        driver_cost = 0.0
        if include_driver and svc.get("driver_charges_pkr"):
            driver_cost = svc["driver_charges_pkr"] * days
            total += driver_cost

        print("\n" + "=" * 65)
        print("          TRANSPORTATION COST ESTIMATION")
        print("=" * 65)
        print(f"Vehicle:               {svc['service_name']}")
        print(f"Rental Days:           {days} day(s)")
        print(f"Base Vehicle Rate:     PKR {svc['daily_rate_pkr'] * days:,.2f}")
        print(f"Driver Charges:        PKR {driver_cost:,.2f}")
        print(f"Fuel Responsibility:   {svc.get('fuel_policy') or 'Direct by customer'}")
        print("-" * 65)
        print(f"TOTAL ESTIMATED HIRE:  PKR {total:,.2f}")
        print("=" * 65)

        confirm = input("\nConfirm booking record in Oracle? (y/n): ").strip().lower()
        if confirm == "y":
            notes = f"Vehicle: {svc['service_name']}, Days: {days}, Driver: {'Yes' if include_driver else 'No'}"
            ok, bkg_ref, msg = create_booking_record(
                user_id=current_user["user_id"],
                trip_id=current_trip_id,
                service_type="TRANSPORT",
                service_ref_id=svc["service_id"],
                travel_date=travel_date,
                quantity=days,
                unit_price_pkr=svc["daily_rate_pkr"],
                total_cost_pkr=total,
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

def select_and_view_public_routes(routes, dest_name):
    """Lists public transit lines and stations."""
    if not routes:
        print(f"\nNo public mass transit lines registered for {dest_name}.")
        return

    print("\n" + "-" * 70)
    print(f"{'#':<3} | {'ROUTE NAME':<34} | {'FARE':<10} | {'HOURS'}")
    print("-" * 70)
    for idx, r in enumerate(routes, 1):
        print(f"{idx:<3} | {r['route_name'][:34]:<34} | PKR {r['fare_pkr']:<6,.0f} | {r.get('operating_hours') or 'All Day'}")
    print("-" * 70)

    sel = input("\nEnter Route Number to view stations & stops (or 0 to back): ").strip()
    if sel == "0":
        return
    try:
        idx = int(sel) - 1
        if 0 <= idx < len(routes):
            route = routes[idx]
            stops = get_route_stops(route["route_id"])
            print("\n" + "=" * 65)
            print(f"      {route['route_name'].upper()}")
            print("=" * 65)
            print(f"Transit Service:    {route['service_name']} ({route['type_name']})")
            print(f"Terminals:          {route['start_stop']} <---> {route['end_stop']}")
            print(f"Total Distance:     {route.get('total_distance_km') or 'N/A'} km")
            print(f"Standard Ticket:    PKR {route['fare_pkr']:,.2f}")
            print(f"Operating Hours:    {route.get('operating_hours') or '06:00 - 22:00'}")
            print(f"Frequency:          Every {route.get('frequency_minutes') or 10} minutes")
            print("-" * 65)
            print("Key Stations / Stops along Route:")
            if stops:
                for s in stops:
                    lmk = f" (Near: {s['nearby_landmark']})" if s.get('nearby_landmark') else ""
                    print(f"  {s['stop_sequence']:>2}. {s['stop_name']}{lmk}")
            else:
                print("  No intermediate stop points recorded.")
            print("=" * 65)
            input("\nPress Enter to continue...")
        else:
            print("[ERROR]: Invalid number.")
    except ValueError:
        print("[ERROR]: Invalid input.")
