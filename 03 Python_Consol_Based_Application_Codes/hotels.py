"""
Pak Voyage - Hotel and Accommodation Module
Handles hotel browsing, filtering, room configuration, meal options, cost calculations, and booking.
"""

from database import execute_query
from booking import create_booking_record

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_hotels_by_destination(dest_id, category=None, max_budget=None):
    """Retrieves hotels filtered by destination, category, and budget."""
    sql = "SELECT * FROM HOTELS WHERE DESTINATION_ID = :did AND STATUS = 'ACTIVE'"
    params = {"did": dest_id}

    if category:
        sql += " AND UPPER(CATEGORY) = UPPER(:cat)"
        params["cat"] = category
    if max_budget:
        sql += " AND PRICE_PER_NIGHT_BASE <= :mb"
        params["mb"] = max_budget

    sql += " ORDER BY RATING DESC, PRICE_PER_NIGHT_BASE ASC"
    return execute_query(sql, params)

def get_hotel_rooms(hotel_id):
    """Retrieves room types for a hotel."""
    sql = "SELECT * FROM HOTEL_ROOMS WHERE HOTEL_ID = :hid ORDER BY PRICE_PER_NIGHT ASC"
    return execute_query(sql, {"hid": hotel_id})

def get_hotel_facilities(hotel_id):
    """Retrieves facilities available at a hotel."""
    sql = "SELECT * FROM HOTEL_FACILITIES WHERE HOTEL_ID = :hid ORDER BY IS_CHARGEABLE ASC"
    return execute_query(sql, {"hid": hotel_id})

def display_hotels_menu(dest_id, dest_name, current_user=None, current_trip_id=None):
    """Interactive hotel catalog menu."""
    while True:
        print("\n" + "=" * 65)
        print(f"      {GREEN}{BOLD}HOTELS & ACCOMMODATIONS - {dest_name.upper()}{RESET}")
        print("=" * 65)
        print("1. View All Verified Hotels")
        print("2. Filter Hotels by Category (Luxury, 5-Star, Budget, Resort, etc.)")
        print("3. Filter Hotels by Maximum Nightly Budget")
        print("4. Compare Two Hotels")
        print("0. Back to Destination Menu")
        print("-" * 65)

        choice = input("Select an option: ").strip()

        if choice == "1":
            hotels = get_hotels_by_destination(dest_id)
            select_and_view_hotel(hotels, dest_name, current_user, current_trip_id)
        elif choice == "2":
            print("\nAvailable Categories: Luxury | 5-Star | 4-Star | 3-Star | Budget | Guest House | Resort | Campsite | Boutique")
            cat = input("Enter Category: ").strip()
            hotels = get_hotels_by_destination(dest_id, category=cat)
            select_and_view_hotel(hotels, dest_name, current_user, current_trip_id)
        elif choice == "3":
            try:
                b = float(input("\nEnter Maximum Price Per Night (PKR): ").strip())
                hotels = get_hotels_by_destination(dest_id, max_budget=b)
                select_and_view_hotel(hotels, dest_name, current_user, current_trip_id)
            except ValueError:
                print("[ERROR]: Please enter a valid numeric budget.")
        elif choice == "4":
            compare_two_hotels(dest_id)
        elif choice == "0":
            break
        else:
            print("[ERROR]: Invalid selection.")

def select_and_view_hotel(hotels, dest_name, current_user, current_trip_id):
    """Lists hotels and allows inspecting rooms and booking."""
    if not hotels:
        print(f"\nNo hotels matched your criteria in {dest_name}.")
        return

    print("\n" + "-" * 65)
    print(f"{'#':<3} | {'HOTEL NAME':<28} | {'CATEGORY':<12} | {'BASE RATE':<12} | {'RATING'}")
    print("-" * 65)
    for idx, h in enumerate(hotels, 1):
        print(f"{idx:<3} | {h['hotel_name'][:28]:<28} | {h['category'][:12]:<12} | PKR {h['price_per_night_base']:<8,.0f} | {h['rating']} / 5.0")
    print("-" * 65)

    sel = input("\nEnter Hotel Number to view details and book (or 0 to back): ").strip()
    if sel == "0":
        return
    try:
        idx = int(sel) - 1
        if 0 <= idx < len(hotels):
            hotel = hotels[idx]
            display_hotel_full_details(hotel, current_user, current_trip_id)
        else:
            print("[ERROR]: Invalid number.")
    except ValueError:
        print("[ERROR]: Invalid input.")

def display_hotel_full_details(hotel, current_user, current_trip_id):
    """Shows full hotel profile, room options, facilities, and booking calculator."""
    print("\n" + "=" * 65)
    print(f"      {hotel['hotel_name'].upper()} ({hotel['category']})")
    print("=" * 65)
    print(f"Address:            {hotel['address']}")
    print(f"Phone:              {hotel.get('contact_phone') or 'Available on Booking'}")
    print(f"Rating:             {hotel['rating']} / 5.0 (Source: {hotel.get('rating_source') or 'Verified'})")
    print(f"Base Rate:          PKR {hotel['price_per_night_base']:,.2f} per night")
    print(f"Price Status:       Verified ({hotel.get('price_source') or 'Official'})")
    print(f"Last Verified:      {hotel.get('last_verified_date') or 'Current Season'}")

    facilities = get_hotel_facilities(hotel["hotel_id"])
    if facilities:
        print("\nAvailable Facilities:")
        for f in facilities:
            chrg = f" (+PKR {f['extra_cost_pkr']:,.0f})" if f["is_chargeable"] == "YES" else " (Included)"
            print(f"  - {f['facility_name']}{chrg}")

    rooms = get_hotel_rooms(hotel["hotel_id"])
    print("\nAvailable Room Types:")
    print("-" * 65)
    for idx, r in enumerate(rooms, 1):
        bfast = "Yes" if r["breakfast_included"] == "YES" else "No"
        dinner = "Yes" if r["dinner_included"] == "YES" else "No"
        print(f"  [{idx}] {r['room_type']}")
        print(f"      Beds: {r['bed_config']} | Capacity: {r['room_capacity']} Guests")
        print(f"      Rate: PKR {r['price_per_night']:,.2f} / night | Breakfast: {bfast} | Dinner: {dinner}")
    print("-" * 65)

    if not current_user:
        print("\n[NOTE]: You must be signed in as a tourist to create a booking.")
        input("Press Enter to continue...")
        return

    book_opt = input("\nWould you like to book a room at this hotel? (y/n): ").strip().lower()
    if book_opt != "y":
        return

    # Booking flow
    try:
        room_sel = int(input("Select Room Type Number (1, 2, ...): ").strip())
        if room_sel < 1 or room_sel > len(rooms):
            print("[ERROR]: Invalid room selection.")
            return
        selected_room = rooms[room_sel - 1]

        nights = int(input("Number of Nights: ").strip())
        num_rooms = int(input("Number of Rooms required: ").strip())
        num_guests = int(input("Number of Guests: ").strip())
        check_in = input("Check-in Date (YYYY-MM-DD): ").strip()
        check_out = input("Check-out Date (YYYY-MM-DD): ").strip()

        if nights <= 0 or num_rooms <= 0 or num_guests <= 0:
            print("[ERROR]: Values must be positive numbers.")
            return

        # Meal options
        add_breakfast = input("Add Daily Buffet Breakfast (+PKR 1,200/guest/night)? (y/n): ").strip().lower() == "y"
        add_dinner = input("Add Daily Buffet Dinner (+PKR 2,000/guest/night)? (y/n): ").strip().lower() == "y"

        base_room_cost = selected_room["price_per_night"] * nights * num_rooms
        meal_cost = 0.0
        if add_breakfast:
            meal_cost += 1200.0 * num_guests * nights
        if add_dinner:
            meal_cost += 2000.0 * num_guests * nights

        total_est = base_room_cost + meal_cost

        # Display booking summary
        print("\n" + "=" * 65)
        print("                 BOOKING ESTIMATION SUMMARY")
        print("=" * 65)
        print(f"Hotel:                 {hotel['hotel_name']}")
        print(f"Room Type:             {selected_room['room_type']}")
        print(f"Duration:              {nights} Night(s) ({check_in} to {check_out})")
        print(f"Rooms / Guests:        {num_rooms} Room(s) for {num_guests} Guest(s)")
        print(f"Base Room Cost:        PKR {base_room_cost:,.2f}")
        print(f"Meal Add-ons:          PKR {meal_cost:,.2f}")
        print("-" * 65)
        print(f"TOTAL ESTIMATED COST:  PKR {total_est:,.2f}")
        print("=" * 65)
        print("IMPORTANT ACADEMIC NOTICE:")
        print("This creates an official academic application booking record in Oracle.")
        print("It does not represent an external hotel reservation payment.")
        print("=" * 65)

        confirm = input("\nConfirm and record this booking in Oracle? (y/n): ").strip().lower()
        if confirm == "y":
            notes = f"Room: {selected_room['room_type']}, {nights} nights, {num_rooms} rooms. CheckIn: {check_in}, CheckOut: {check_out}"
            success, bkg_ref, msg = create_booking_record(
                user_id=current_user["user_id"],
                trip_id=current_trip_id,
                service_type="HOTEL",
                service_ref_id=hotel["hotel_id"],
                travel_date=check_in,
                quantity=num_rooms,
                unit_price_pkr=selected_room["price_per_night"],
                total_cost_pkr=total_est,
                notes=notes
            )
            if success:
                print(f"\n[SUCCESS]: {msg}")
                print(f"Your Unique Booking Reference: {bkg_ref}")
            else:
                print(f"\n[FAILED]: {msg}")
            input("\nPress Enter to continue...")
    except ValueError:
        print("[ERROR]: Invalid numeric input.")

def compare_two_hotels(dest_id):
    """Compares two hotels side-by-side."""
    hotels = get_hotels_by_destination(dest_id)
    if len(hotels) < 2:
        print("\nNot enough hotels available for comparison in this destination.")
        return

    print("\nSelect Two Hotels to Compare:")
    for idx, h in enumerate(hotels, 1):
        print(f"  {idx}. {h['hotel_name']} ({h['category']} - PKR {h['price_per_night_base']:,.0f})")

    try:
        h1 = int(input("\nSelect First Hotel: ").strip())
        h2 = int(input("Select Second Hotel: ").strip())
        if h1 < 1 or h1 > len(hotels) or h2 < 1 or h2 > len(hotels) or h1 == h2:
            print("[ERROR]: Invalid selection.")
            return

        hotel1 = hotels[h1 - 1]
        hotel2 = hotels[h2 - 1]

        p1_str = f"PKR {hotel1['price_per_night_base']:,.0f}"
        p2_str = f"PKR {hotel2['price_per_night_base']:,.0f}"
        r1_str = f"{hotel1['rating']} / 5.0"
        r2_str = f"{hotel2['rating']} / 5.0"

        print("\n" + "=" * 70)
        print(f"{'CRITERIA':<25} | {hotel1['hotel_name'][:20]:<20} | {hotel2['hotel_name'][:20]:<20}")
        print("=" * 70)
        print(f"{'Category':<25} | {hotel1['category']:<20} | {hotel2['category']:<20}")
        print(f"{'Base Rate / Night':<25} | {p1_str:<20} | {p2_str:<20}")
        print(f"{'Rating':<25} | {r1_str:<20} | {r2_str:<20}")
        print(f"{'Address':<25} | {hotel1['address'][:20]:<20} | {hotel2['address'][:20]:<20}")
        print("=" * 70)
        input("\nPress Enter to continue...")
    except ValueError:
        print("[ERROR]: Invalid input.")
