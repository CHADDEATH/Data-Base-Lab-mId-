"""
Pak Voyage - Administrator Management & Analytical Reporting Module
Provides complete oversight: User travel histories, analytical SQL reports, tourism CRUD, and DB metrics.
"""

from database import execute_query, execute_non_query
from authentication import change_admin_password
from data_import import run_import

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

def display_admin_dashboard(admin_user):
    """Main administrative console loop."""
    while True:
        print("\n========================================================================")
        print(f"               {GREEN}{BOLD}PAK VOYAGE - ADMINISTRATOR MANAGEMENT CONSOLE{RESET}")
        print(f"               Logged in: {admin_user['full_name']} (@{admin_user['username']})")
        print("========================================================================")
        print("  [1]  View Registered Users")
        print("  [2]  Search Individual User Profile")
        print("  [3]  View All Planned Trips Across Users")
        print("  [4]  View All System Bookings & Vouchers")
        print("  [5]  User Chronological Travel History (Viva Audit Transcript)")
        print("  [6]  Financial & Analytical Revenue Reports (SQL Joins / Aggregates)")
        print("  [7]  Destination Popularity & Attraction Statistics")
        print("  [8]  Manage Tourism Records (Add / Update Hotels, Landmarks, Trails)")
        print("  [9]  Database Table Record Inventory & Live Counts")
        print("  [10] Run / Refresh Excel ETL Data Import")
        print("  [11] Change Administrator Password")
        print("  [0]  Logout Administrator")
        print("------------------------------------------------------------------------")

        choice = input("Enter choice [0-11]: ").strip()

        if choice == "1":
            view_registered_users()
        elif choice == "2":
            search_user_profile()
        elif choice == "3":
            view_all_trips()
        elif choice == "4":
            view_all_bookings()
        elif choice == "5":
            generate_user_travel_history()
        elif choice == "6":
            display_financial_reports()
        elif choice == "7":
            display_destination_statistics()
        elif choice == "8":
            manage_tourism_records_menu()
        elif choice == "9":
            display_database_counts()
        elif choice == "10":
            run_import()
            input("\nPress Enter to continue...")
        elif choice == "11":
            old_p = input("\nEnter Current Password: ").strip()
            new_p = input("Enter New Password: ").strip()
            cnf_p = input("Confirm New Password: ").strip()
            ok, msg = change_admin_password(admin_user["admin_id"], old_p, new_p, cnf_p)
            print(f"\n{msg}")
            input("Press Enter to continue...")
        elif choice == "0":
            print("\nLogging out administrator session.")
            break
        else:
            print("[ERROR]: Invalid selection.")

def view_registered_users():
    """Displays all registered tourists."""
    sql = "SELECT USER_ID, FULL_NAME, USERNAME, AGE, COUNTRY, EMAIL, CREATED_AT, STATUS FROM USERS ORDER BY USER_ID ASC"
    users = execute_query(sql)
    print("\n" + "=" * 75)
    print("                 REGISTERED TOURIST ACCOUNTS")
    print("=" * 75)
    if not users:
        print("No user accounts registered yet.")
    else:
        print(f"{'ID':<4} | {'NAME':<20} | {'USERNAME':<14} | {'AGE':<4} | {'COUNTRY':<12} | {'EMAIL'}")
        print("-" * 75)
        for u in users:
            print(f"{u['user_id']:<4} | {u['full_name'][:20]:<20} | {u['username'][:14]:<14} | {u['age']:<4} | {u['country'][:12]:<12} | {u['email']}")
    print("=" * 75)
    input("\nPress Enter to continue...")

def search_user_profile():
    """Searches for a specific tourist by username or email."""
    q = input("\nEnter username or email to search: ").strip()
    sql = """
        SELECT USER_ID, FULL_NAME, USERNAME, AGE, COUNTRY, EMAIL, CREATED_AT, STATUS
        FROM USERS
        WHERE LOWER(USERNAME) LIKE LOWER(:q) OR LOWER(EMAIL) LIKE LOWER(:q)
    """
    results = execute_query(sql, {"q": f"%{q}%"})
    print("\n" + "=" * 65)
    print("                 USER SEARCH RESULTS")
    print("=" * 65)
    if not results:
        print("No matching user accounts found.")
    else:
        for u in results:
            reg_date = str(u.get('created_at') or '').split()[0]
            print(f"User ID:           {u['user_id']}")
            print(f"Full Name:         {u['full_name']}")
            print(f"Username:          {u['username']}")
            print(f"Age / Country:     {u['age']} Years | {u['country']}")
            print(f"Email:             {u['email']}")
            print(f"Registered On:     {reg_date}")
            print(f"Account Status:    {u['status']}")
            print("-" * 65)
    input("\nPress Enter to continue...")

def view_all_trips():
    """Displays all planned trips system-wide."""
    sql = """
        SELECT t.TRIP_ID, u.USERNAME, t.TRIP_NAME, t.START_DATE, t.END_DATE, 
               t.NUM_TRAVELLERS, t.BUDGET_PKR, t.STATUS
        FROM TRIPS t
        JOIN USERS u ON t.USER_ID = u.USER_ID
        ORDER BY t.START_DATE DESC
    """
    trips = execute_query(sql)
    print("\n" + "=" * 75)
    print("                 SYSTEM-WIDE TOURIST TRIPS")
    print("=" * 75)
    if not trips:
        print("No trips planned in the system yet.")
    else:
        print(f"{'ID':<4} | {'USER':<12} | {'TRIP NAME':<26} | {'DATES':<22} | {'BUDGET'}")
        print("-" * 75)
        for t in trips:
            sdate = str(t.get('start_date') or '').split()[0]
            edate = str(t.get('end_date') or '').split()[0]
            dates_str = f"{sdate} to {edate}"
            print(f"{t['trip_id']:<4} | {t['username'][:12]:<12} | {t['trip_name'][:26]:<26} | {dates_str:<22} | PKR {t['budget_pkr']:<8,.0f}")
    print("=" * 75)
    input("\nPress Enter to continue...")

def view_all_bookings():
    """Displays all service bookings system-wide."""
    sql = """
        SELECT b.BOOKING_ID, b.BOOKING_REF, u.USERNAME, b.SERVICE_TYPE, 
               b.TRAVEL_DATE, b.TOTAL_COST_PKR, b.BOOKING_STATUS, b.PAYMENT_STATUS
        FROM BOOKINGS b
        JOIN USERS u ON b.USER_ID = u.USER_ID
        ORDER BY b.BOOKING_DATE DESC
    """
    bookings = execute_query(sql)
    print("\n" + "=" * 80)
    print("                 ALL SYSTEM SERVICE BOOKINGS")
    print("=" * 80)
    if not bookings:
        print("No bookings recorded in the system yet.")
    else:
        print(f"{'REF':<15} | {'USER':<12} | {'TYPE':<10} | {'DATE':<12} | {'TOTAL':<12} | {'STATUS':<10} | {'PAYMENT'}")
        print("-" * 80)
        for b in bookings:
            tdate = str(b.get('travel_date') or '').split()[0]
            print(f"{b['booking_ref']:<15} | {b['username'][:12]:<12} | {b['service_type']:<10} | {tdate:<12} | PKR {b['total_cost_pkr']:<8,.0f} | {b['booking_status']:<10} | {b['payment_status']}")
    print("=" * 80)
    input("\nPress Enter to continue...")

def generate_user_travel_history():
    """
    MAJOR ADMIN FEATURE:
    Selects any registered tourist and dynamically generates their complete chronological
    travel history transcript directly from Oracle relational tables.
    """
    users = execute_query("SELECT USER_ID, USERNAME, FULL_NAME, EMAIL FROM USERS ORDER BY USER_ID ASC")
    if not users:
        print("\nNo registered users available.")
        return

    print("\nSelect User to Generate Complete Travel History:")
    for idx, u in enumerate(users, 1):
        print(f"  {idx}. {u['full_name']} (@{u['username']} - {u['email']})")

    try:
        u_sel = int(input("\nUser Number: ").strip()) - 1
        if not (0 <= u_sel < len(users)):
            print("[ERROR]: Invalid selection.")
            return
        user = users[u_sel]
        uid = user["user_id"]

        # Fetch Full User Record
        u_full = execute_query("SELECT * FROM USERS WHERE USER_ID = :id", {"id": uid})[0]

        print("\n" + "=" * 75)
        print("       PAK VOYAGE - CHRONOLOGICAL USER TRAVEL HISTORY REPORT")
        print("=" * 75)
        print("1. USER PROFILE AUDIT")
        print("-" * 75)
        print(f"Full Name:            {u_full['full_name']}")
        print(f"Username:             {u_full['username']}")
        print(f"Age:                  {u_full['age']} Years")
        print(f"Country of Origin:    {u_full['country']}")
        print(f"Email:                {u_full['email']}")
        print(f"Registration Date:    {str(u_full.get('created_at') or '').split()[0]}")
        print(f"Account Status:       {u_full['status']}")
        print("Password Hash:        [PROTECTED - NEVER DISPLAYED]")

        # Fetch Trips
        trips = execute_query("SELECT * FROM TRIPS WHERE USER_ID = :id ORDER BY START_DATE ASC", {"id": uid})
        print("\n" + "-" * 75)
        print(f"2. TRIP HISTORY ({len(trips)} Recorded Journeys)")
        print("-" * 75)
        if not trips:
            print("  No multi-destination trips planned yet by this user.")
        else:
            for t in trips:
                sdate = str(t.get('start_date') or '').split()[0]
                edate = str(t.get('end_date') or '').split()[0]
                print(f"\n  * Trip #{t['trip_id']}: '{t['trip_name']}'")
                print(f"    Dates: {sdate} to {edate} | Travellers: {t['num_travellers']} ({t['num_adults']} Adults, {t['num_children']} Children)")
                print(f"    Planned Budget: PKR {t['budget_pkr']:,.2f} | Status: {t['status']}")
                print(f"    Preferences:    {t.get('travel_preferences') or 'None'}")

                # Destinations in this trip
                dest_sql = """
                    SELECT td.VISIT_ORDER, td.STAY_DAYS, d.DESTINATION_NAME, d.PROVINCE_REGION
                    FROM TRIP_DESTINATIONS td
                    JOIN DESTINATIONS d ON td.DESTINATION_ID = d.DESTINATION_ID
                    WHERE td.TRIP_ID = :tid
                    ORDER BY td.VISIT_ORDER ASC
                """
                dests = execute_query(dest_sql, {"tid": t["trip_id"]})
                if dests:
                    print("    Route Sequence:")
                    for d in dests:
                        print(f"      - Stop #{d['visit_order']}: {d['destination_name']} ({d['stay_days']} days)")

                # Day-wise Itinerary
                itin_sql = """
                    SELECT ti.DAY_NUMBER, ti.TIME_SLOT, ti.ITEM_TYPE, ti.ITEM_TITLE, ti.EST_COST_PKR
                    FROM TRIP_ITINERARY ti
                    WHERE ti.TRIP_ID = :tid
                    ORDER BY ti.DAY_NUMBER ASC
                """
                itinerary = execute_query(itin_sql, {"tid": t["trip_id"]})
                if itinerary:
                    print("    Scheduled Itinerary Items:")
                    for it in itinerary:
                        print(f"      * Day {it['day_number']} [{it['time_slot']}]: {it['item_title']} ({it['item_type']}) - PKR {it['est_cost_pkr']:,.0f}")

        # Fetch Bookings
        bkg_sql = "SELECT * FROM BOOKINGS WHERE USER_ID = :id ORDER BY BOOKING_DATE ASC"
        bookings = execute_query(bkg_sql, {"id": uid})
        print("\n" + "-" * 75)
        print(f"3. BOOKING TRANSACTIONS ({len(bookings)} Total Bookings)")
        print("-" * 75)
        if not bookings:
            print("  No service booking records found.")
        else:
            for b in bookings:
                tdate = str(b.get('travel_date') or '').split()[0]
                print(f"  * Reference: {b['booking_ref']}")
                print(f"    Service: {b['service_type']} (ID #{b['service_ref_id']}) | Travel Date: {tdate}")
                print(f"    Quantity: {b['quantity']} | Total: PKR {b['total_cost_pkr']:,.2f}")
                print(f"    Booking Status: {b['booking_status']} | Payment: {b['payment_status']}")
                print(f"    Notes: {b.get('notes') or 'None'}")

        # Fetch Financial Summary
        exp_sql = "SELECT NVL(SUM(AMOUNT_PKR), 0) AS TOT FROM TRIP_EXPENSES WHERE USER_ID = :id"
        tot_exp = execute_query(exp_sql, {"id": uid})[0]["tot"]

        pay_sql = "SELECT NVL(SUM(AMOUNT_PKR), 0) AS TOT FROM PAYMENTS WHERE USER_ID = :id"
        tot_pay = execute_query(pay_sql, {"id": uid})[0]["tot"]

        bkg_tot_sql = "SELECT NVL(SUM(TOTAL_COST_PKR), 0) AS TOT FROM BOOKINGS WHERE USER_ID = :id AND BOOKING_STATUS != 'Cancelled'"
        tot_bkg_val = execute_query(bkg_tot_sql, {"id": uid})[0]["tot"]

        print("\n" + "-" * 75)
        print("4. COMPLETE FINANCIAL RECONCILIATION SUMMARY")
        print("-" * 75)
        print(f"Confirmed Bookings Value:     PKR {tot_bkg_val:,.2f}")
        print(f"Actual Payments Settled:      PKR {tot_pay:,.2f}")
        print(f"Recorded Out-of-Pocket Exp:   PKR {tot_exp:,.2f}")
        print(f"Combined User Spend Footprint:PKR {(tot_bkg_val + tot_exp):,.2f}")
        print("=" * 75)
        input("\nPress Enter to return to Admin Dashboard...")
    except ValueError:
        print("[ERROR]: Invalid input.")

def display_financial_reports():
    """Displays comprehensive analytical SQL reports."""
    print("\n" + "=" * 70)
    print("      ADMINISTRATIVE FINANCIAL & ANALYTICAL DATABASE REPORTS")
    print("=" * 70)

    # 1. Platform Totals
    kpi_sql = """
        SELECT 
            (SELECT COUNT(*) FROM USERS WHERE STATUS = 'ACTIVE') AS USERS,
            (SELECT COUNT(*) FROM TRIPS) AS TRIPS,
            (SELECT COUNT(*) FROM BOOKINGS WHERE BOOKING_STATUS = 'Confirmed') AS CONFIRMED_BKG,
            (SELECT COUNT(*) FROM BOOKINGS WHERE BOOKING_STATUS = 'Cancelled') AS CANCELLED_BKG,
            (SELECT NVL(SUM(TOTAL_COST_PKR), 0) FROM BOOKINGS WHERE BOOKING_STATUS = 'Confirmed') AS GROSS_BKG_VAL,
            (SELECT NVL(SUM(AMOUNT_PKR), 0) FROM PAYMENTS WHERE PAYMENT_STATUS = 'Recorded') AS SETTLED_PAYMENTS
        FROM DUAL
    """
    kpis = execute_query(kpi_sql)[0]
    print("PLATFORM KEY PERFORMANCE INDICATORS:")
    print(f"  - Active Tourists:             {kpis['users']}")
    print(f"  - Total Trips Created:         {kpis['trips']}")
    print(f"  - Confirmed Bookings:          {kpis['confirmed_bkg']}")
    print(f"  - Cancelled Bookings:          {kpis['cancelled_bkg']}")
    print(f"  - Estimated Booking Value:     PKR {kpis['gross_bkg_val']:,.2f}")
    print(f"  - Settled Payment Collection:  PKR {kpis['settled_payments']:,.2f}")
    print("-" * 70)

    # 2. Average Hotel Rates by Category
    cat_sql = """
        SELECT CATEGORY, COUNT(*) AS PROPS, ROUND(AVG(PRICE_PER_NIGHT_BASE), 0) AS AVG_PRICE, ROUND(AVG(RATING), 1) AS AVG_RAT
        FROM HOTELS
        GROUP BY CATEGORY
        ORDER BY AVG_PRICE DESC
    """
    hotel_cats = execute_query(cat_sql)
    print("HOTEL ACCOMMODATION BENCHMARKS BY CATEGORY:")
    for h in hotel_cats:
        print(f"  - {h['category']:<14}: {h['props']:>2} hotels | Avg: PKR {h['avg_price']:>7,.0f}/night | Rating: {h['avg_rat']} / 5.0")
    print("-" * 70)

    # 3. Trails Distribution by Difficulty
    trail_sql = """
        SELECT DIFFICULTY_LEVEL, COUNT(*) AS CNT, ROUND(AVG(DISTANCE_KM), 1) AS AVG_DIST
        FROM TRAILS
        GROUP BY DIFFICULTY_LEVEL
    """
    trails_stat = execute_query(trail_sql)
    print("TRAILS & TREKKING ROUTE SPREAD:")
    for t in trails_stat:
        print(f"  - {t['difficulty_level']:<12}: {t['cnt']:>2} routes | Avg Distance: {t['avg_dist']} km")
    print("=" * 70)
    input("\nPress Enter to continue...")

def display_destination_statistics():
    """Displays statistics by destination using VW_DESTINATION_SUMMARY."""
    sql = "SELECT * FROM VW_DESTINATION_SUMMARY ORDER BY DESTINATION_ID ASC"
    stats = execute_query(sql)
    print("\n" + "=" * 80)
    print("                 DESTINATION METRICS & RECORD COUNTS")
    print("=" * 80)
    print(f"{'DESTINATION':<24} | {'HOTELS':<7} | {'LANDMARKS':<10} | {'TRAILS':<7} | {'ACTIVITIES':<11} | {'FOOD'}")
    print("-" * 80)
    for s in stats:
        print(f"{s['destination_name'][:24]:<24} | {s['total_hotels']:<7} | {s['total_landmarks']:<10} | {s['total_trails']:<7} | {s['total_activities']:<11} | {s['total_restaurants']}")
    print("=" * 80)
    input("\nPress Enter to continue...")

def display_database_counts():
    """Queries user_tables to show record counts across all 28 tables."""
    sql = """
        SELECT table_name 
        FROM user_tables 
        ORDER BY table_name ASC
    """
    tables = execute_query(sql)
    print("\n" + "=" * 65)
    print("      ORACLE DATABASE RECORD COUNTS (LIVE INVENTORY)")
    print("=" * 65)
    total_rows = 0
    for t in tables:
        tname = t["table_name"]
        cnt_sql = f"SELECT COUNT(*) AS CNT FROM {tname}"
        cnt = execute_query(cnt_sql)[0]["cnt"]
        total_rows += cnt
        print(f"  {tname:<32} : {cnt:>6} records")
    print("-" * 65)
    print(f"  COMBINED DATABASE ROWS        : {total_rows:>6} rows")
    print("=" * 65)
    input("\nPress Enter to continue...")

def manage_tourism_records_menu():
    """Menu allowing admin to add or update tourism records."""
    print("\n" + "=" * 65)
    print("      MANAGE TOURISM RECORDS (ADMIN CRUD)")
    print("=" * 65)
    print("1. Add New Verified Hotel")
    print("2. Add New Cultural Landmark")
    print("3. Add New Hiking / Trekking Trail")
    print("4. Update Service Price or Fee")
    print("0. Back to Admin Console")
    print("-" * 65)

    ch = input("Select: ").strip()
    if ch == "1":
        add_new_hotel()
    elif ch == "2":
        add_new_landmark()
    elif ch == "3":
        add_new_trail()
    elif ch == "4":
        update_price_record()

def add_new_hotel():
    """Adds a new hotel into HOTELS table."""
    try:
        did = int(input("\nDestination ID (1-Islamabad, 2-Lahore, 3-Karachi, 4-Skardu, 5-Kashmir): ").strip())
        name = input("Hotel Name: ").strip()
        cat = input("Category (Luxury, 5-Star, 4-Star, 3-Star, Budget, Resort, Campsite): ").strip()
        addr = input("Address: ").strip()
        price = float(input("Base Price Per Night (PKR): ").strip())

        sql = """
            INSERT INTO HOTELS (DESTINATION_ID, HOTEL_NAME, CATEGORY, ADDRESS, PRICE_PER_NIGHT_BASE, RATING, STATUS)
            VALUES (:did, :name, :cat, :addr, :price, 4.0, 'ACTIVE')
        """
        ok, _, err = execute_non_query(sql, {"did": did, "name": name, "cat": cat, "addr": addr, "price": price})
        if ok:
            print(f"\n[SUCCESS]: Hotel '{name}' successfully inserted into Oracle.")
        else:
            print(f"[ERROR]: {err}")
    except ValueError:
        print("[ERROR]: Invalid input.")
    input("Press Enter to continue...")

def add_new_landmark():
    """Adds a new landmark into LANDMARKS table."""
    try:
        did = int(input("\nDestination ID (1-5): ").strip())
        name = input("Landmark Name: ").strip()
        cat = input("Category: ").strip()
        desc = input("Description: ").strip()
        loc = input("Location Address: ").strip()
        adult_fee = float(input("Adult Entry Fee (PKR, or 0): ").strip() or "0")

        sql = """
            INSERT INTO LANDMARKS (DESTINATION_ID, LANDMARK_NAME, CATEGORY, DESCRIPTION, LOCATION_ADDRESS, ENTRY_FEE_ADULT_PKR)
            VALUES (:did, :name, :cat, :desc, :loc, :fee)
        """
        ok, _, err = execute_non_query(sql, {"did": did, "name": name, "cat": cat, "desc": desc, "loc": loc, "fee": adult_fee})
        if ok:
            print(f"\n[SUCCESS]: Landmark '{name}' successfully inserted into Oracle.")
        else:
            print(f"[ERROR]: {err}")
    except ValueError:
        print("[ERROR]: Invalid input.")
    input("Press Enter to continue...")

def add_new_trail():
    """Adds a new trail into TRAILS table."""
    try:
        did = int(input("\nDestination ID (1-5): ").strip())
        name = input("Trail Name: ").strip()
        dist_name = input("District: ").strip()
        start_pt = input("Starting Point: ").strip()
        end_pt = input("Ending Point: ").strip()
        distance = float(input("Distance in KM: ").strip())
        duration = input("Duration (e.g. 3 Hours): ").strip()
        diff = input("Difficulty (Easy / Moderate / Difficult / Extreme): ").strip()
        season = input("Recommended Season: ").strip()

        sql = """
            INSERT INTO TRAILS (
                DESTINATION_ID, TRAIL_NAME, DISTRICT, STARTING_POINT, ENDING_POINT, 
                DISTANCE_KM, DURATION_TEXT, DIFFICULTY_LEVEL, BEST_SEASON, BASE_ENTRY_FEE_PKR
            ) VALUES (
                :did, :name, :dist, :spt, :ept, :distkm, :dur, :diff, :seas, 0.0
            )
        """
        ok, _, err = execute_non_query(sql, {
            "did": did, "name": name, "dist": dist_name, "spt": start_pt,
            "ept": end_pt, "distkm": distance, "dur": duration, "diff": diff, "seas": season
        })
        if ok:
            print(f"\n[SUCCESS]: Trail '{name}' successfully inserted into Oracle.")
        else:
            print(f"[ERROR]: {err}")
    except ValueError:
        print("[ERROR]: Invalid input.")
    input("Press Enter to continue...")

def update_price_record():
    """Allows updating hotel or activity prices."""
    print("\nSelect Entity to Update Price:")
    print("1. Update Hotel Base Rate")
    print("2. Update Activity Price")
    c = input("Choice: ").strip()
    try:
        if c == "1":
            hid = int(input("Enter Hotel ID: ").strip())
            new_p = float(input("New Price Per Night (PKR): ").strip())
            sql = "UPDATE HOTELS SET PRICE_PER_NIGHT_BASE = :p, LAST_VERIFIED_DATE = SYSDATE WHERE HOTEL_ID = :id"
            ok, _, err = execute_non_query(sql, {"p": new_p, "id": hid})
            if ok:
                print(f"[SUCCESS]: Hotel #{hid} price updated to PKR {new_p:,.2f}.")
            else:
                print(f"[ERROR]: {err}")
        elif c == "2":
            aid = int(input("Enter Activity ID: ").strip())
            new_p = float(input("New Price (PKR): ").strip())
            sql = "UPDATE ACTIVITIES SET PRICE_PKR = :p, LAST_VERIFIED_DATE = SYSDATE WHERE ACTIVITY_ID = :id"
            ok, _, err = execute_non_query(sql, {"p": new_p, "id": aid})
            if ok:
                print(f"[SUCCESS]: Activity #{aid} price updated to PKR {new_p:,.2f}.")
            else:
                print(f"[ERROR]: {err}")
    except ValueError:
        print("[ERROR]: Invalid numeric input.")
    input("Press Enter to continue...")
