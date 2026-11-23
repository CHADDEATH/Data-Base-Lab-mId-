"""
Pak Voyage - Restaurants & Regional Gastronomy Module
Covers Food Streets, Regional Specialties (Balti, Kashmiri, Mughlai, Karahi), and Meal Cost Estimator.
"""

from database import execute_query

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_restaurants_by_destination(dest_id, price_cat=None):
    """Retrieves restaurants for a destination."""
    sql = "SELECT * FROM RESTAURANTS WHERE DESTINATION_ID = :did"
    params = {"did": dest_id}
    if price_cat:
        sql += " AND UPPER(PRICE_CATEGORY) = UPPER(:pcat)"
        params["pcat"] = price_cat
    sql += " ORDER BY RATING DESC, RESTAURANT_NAME ASC"
    return execute_query(sql, params)

def get_restaurant_menu(restaurant_id):
    """Retrieves dishes and food items for a restaurant."""
    sql = "SELECT * FROM FOOD_ITEMS WHERE RESTAURANT_ID = :rid ORDER BY IS_LOCAL_SPECIALTY DESC, PRICE_PKR ASC"
    return execute_query(sql, {"rid": restaurant_id})

def display_restaurants_menu(dest_id, dest_name):
    """Interactive restaurants and gastronomy menu."""
    while True:
        print("\n" + "=" * 65)
        print(f"      {GREEN}{BOLD}RESTAURANTS & LOCAL FOOD - {dest_name.upper()}{RESET}")
        print("=" * 65)
        print("1. Browse All Restaurants & Food Streets")
        print("2. Filter by Price Category (Budget, Moderate, Fine Dining, Street Food)")
        print("3. View Regional Specialties Only")
        print("0. Back to Destination Menu")
        print("-" * 65)

        choice = input("Select an option: ").strip()

        if choice == "1":
            rests = get_restaurants_by_destination(dest_id)
            select_and_view_restaurant(rests)
        elif choice == "2":
            pcat = input("\nEnter category (Budget, Moderate, Fine Dining, Street Food): ").strip()
            rests = get_restaurants_by_destination(dest_id, price_cat=pcat)
            select_and_view_restaurant(rests)
        elif choice == "3":
            sql = """
                SELECT DISTINCT r.* 
                FROM RESTAURANTS r
                JOIN FOOD_ITEMS f ON r.RESTAURANT_ID = f.RESTAURANT_ID
                WHERE r.DESTINATION_ID = :did AND f.IS_LOCAL_SPECIALTY = 'YES'
                ORDER BY r.RATING DESC
            """
            rests = execute_query(sql, {"did": dest_id})
            select_and_view_restaurant(rests)
        elif choice == "0":
            break
        else:
            print("[ERROR]: Invalid selection.")

def select_and_view_restaurant(restaurants):
    """Lists restaurants and allows viewing menus and estimating meal bills."""
    if not restaurants:
        print("\nNo restaurants found matching your criteria.")
        return

    print("\n" + "-" * 70)
    print(f"{'#':<3} | {'RESTAURANT NAME':<28} | {'FOOD AREA':<18} | {'CATEGORY':<12} | {'RATING'}")
    print("-" * 70)
    for idx, r in enumerate(restaurants, 1):
        print(f"{idx:<3} | {r['restaurant_name'][:28]:<28} | {r['food_area'][:18]:<18} | {r['price_category'][:12]:<12} | {r['rating']} / 5.0")
    print("-" * 70)

    sel = input("\nEnter Restaurant Number to view menu (or 0 to back): ").strip()
    if sel == "0":
        return
    try:
        idx = int(sel) - 1
        if 0 <= idx < len(restaurants):
            display_restaurant_profile(restaurants[idx])
        else:
            print("[ERROR]: Invalid number.")
    except ValueError:
        print("[ERROR]: Invalid input.")

def display_restaurant_profile(restaurant):
    """Displays restaurant profile and itemized meal cost calculator."""
    print("\n" + "=" * 65)
    print(f"      {restaurant['restaurant_name'].upper()}")
    print("=" * 65)
    print(f"Food Area / Street:   {restaurant['food_area']}")
    print(f"Address:              {restaurant['address']}")
    print(f"Cuisine Type:         {restaurant['cuisine_type']}")
    print(f"Price Category:       {restaurant['price_category']}")
    print(f"Rating:               {restaurant['rating']} / 5.0")
    print(f"Opening Hours:        {restaurant.get('opening_hours') or 'Open daily'}")
    print(f"Contact Phone:        {restaurant.get('contact_phone') or 'Available on site'}")
    print("-" * 65)
    print(f"Description:\n  {restaurant['description']}")
    print("-" * 65)

    menu = get_restaurant_menu(restaurant["restaurant_id"])
    if menu:
        print("\nMenu & Regional Specialties:")
        print("-" * 65)
        for idx, item in enumerate(menu, 1):
            spec = " [LOCAL SPECIALTY]" if item["is_local_specialty"] == "YES" else ""
            print(f"  [{idx}] {item['item_name']}{spec}")
            print(f"      Price: PKR {item['price_pkr']:,.2f} | Category: {item.get('dish_type') or 'Dish'}")
            if item.get('description'):
                print(f"      {item['description']}")
        print("-" * 65)

        calc_opt = input("\nCalculate estimated meal bill? (y/n): ").strip().lower()
        if calc_opt == "y":
            calculate_meal_bill(menu)
        else:
            input("\nPress Enter to continue...")
    else:
        print("\nNo specific menu items recorded.")
        input("\nPress Enter to continue...")

def calculate_meal_bill(menu):
    """Calculates meal bill for selected dishes and portions."""
    try:
        num_diners = int(input("\nNumber of Diners / Guests: ").strip())
        print("Select Menu Items (comma-separated numbers, e.g. 1, 2):")
        chosen = input("Items: ").strip()

        total = 0.0
        selected_names = []
        if chosen:
            for part in chosen.split(","):
                part = part.strip()
                if part.isdigit():
                    idx = int(part) - 1
                    if 0 <= idx < len(menu):
                        item = menu[idx]
                        total += item["price_pkr"]
                        selected_names.append(f"{item['item_name']} (PKR {item['price_pkr']:,.0f})")

        print("\n" + "=" * 65)
        print("            ESTIMATED MEAL BILL SUMMARY")
        print("=" * 65)
        for name in selected_names:
            print(f"  - {name}")
        print("-" * 65)
        print(f"Total Food Items:       PKR {total:,.2f}")
        per_person = total / num_diners if num_diners > 0 else total
        print(f"Est. Cost Per Person:   PKR {per_person:,.2f} ({num_diners} diners)")
        print("=" * 65)
        input("\nPress Enter to continue...")
    except ValueError:
        print("[ERROR]: Invalid input.")
