"""
Pak Voyage - Travel Budget & Expense Calculator Module
Tracks planned travel budgets, category-wise expenditure, per-person division, and currency estimates.
"""

from database import execute_query, execute_non_query, execute_insert_returning_id
from trip_planner import get_user_trips

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

EXPENSE_CATEGORIES = [
    'Hotel', 'Food', 'Transport', 'Fuel', 'Activities', 'Trekking/Guide', 
    'Entry Tickets', 'Zoo Tickets', 'Parking', 'Permits', 'Shopping', 'Other'
]

# Real indicative exchange rates for foreign tourists (Reference Date: 2026-03-01)
CURRENCY_RATES_PKR = {
    "USD": 278.50,
    "EUR": 302.20,
    "GBP": 354.10,
    "SAR": 74.25,
    "AED": 75.80
}

def get_trip_expenses(trip_id):
    """Retrieves all expenses recorded for a trip."""
    sql = "SELECT * FROM TRIP_EXPENSES WHERE TRIP_ID = :tid ORDER BY EXPENSE_DATE DESC"
    return execute_query(sql, {"tid": trip_id})

def get_trip_financial_summary(trip_id):
    """Calculates comprehensive financial summary for a trip."""
    trip_sql = "SELECT BUDGET_PKR, NUM_TRAVELLERS FROM TRIPS WHERE TRIP_ID = :tid"
    trip_data = execute_query(trip_sql, {"tid": trip_id})
    if not trip_data:
        return None

    budget = trip_data[0]["budget_pkr"]
    travellers = trip_data[0]["num_travellers"]

    # Confirmed bookings value
    bkg_sql = "SELECT NVL(SUM(TOTAL_COST_PKR), 0) AS VAL FROM BOOKINGS WHERE TRIP_ID = :tid AND BOOKING_STATUS != 'Cancelled'"
    bkg_val = execute_query(bkg_sql, {"tid": trip_id})[0]["val"]

    # Recorded expenses total
    exp_sql = "SELECT NVL(SUM(AMOUNT_PKR), 0) AS VAL FROM TRIP_EXPENSES WHERE TRIP_ID = :tid"
    exp_val = execute_query(exp_sql, {"tid": trip_id})[0]["val"]

    # Category-wise breakdown
    cat_sql = """
        SELECT EXPENSE_CATEGORY, NVL(SUM(AMOUNT_PKR), 0) AS CAT_TOTAL
        FROM TRIP_EXPENSES
        WHERE TRIP_ID = :tid
        GROUP BY EXPENSE_CATEGORY
        ORDER BY CAT_TOTAL DESC
    """
    cat_breakdown = execute_query(cat_sql, {"tid": trip_id})

    total_committed = bkg_val + exp_val
    remaining = budget - total_committed

    return {
        "budget": budget,
        "travellers": travellers,
        "bookings_value": bkg_val,
        "expenses_value": exp_val,
        "total_committed": total_committed,
        "remaining_budget": remaining,
        "cost_per_person": (total_committed / travellers) if travellers > 0 else total_committed,
        "categories": cat_breakdown
    }

def display_budget_dashboard(current_user):
    """Interactive budget management dashboard."""
    trips = get_user_trips(current_user["user_id"])
    if not trips:
        print("\nNo trips found. Please plan a trip first before calculating budget.")
        input("Press Enter to continue...")
        return

    while True:
        print("\n" + "=" * 65)
        print(f"      {GREEN}{BOLD}TRAVEL BUDGET & EXPENSE CALCULATOR - {current_user['full_name'].upper()}{RESET}")
        print("=" * 65)
        print("Select Trip to Manage Finances:")
        for idx, t in enumerate(trips, 1):
            print(f"  {idx}. {t['trip_name']} (Budget: PKR {t['budget_pkr']:,.0f})")
        print("0. Back to Tourist Dashboard")
        print("-" * 65)

        sel = input("Select trip: ").strip()
        if sel == "0":
            break
        try:
            t_idx = int(sel) - 1
            if 0 <= t_idx < len(trips):
                manage_trip_budget(trips[t_idx], current_user)
            else:
                print("[ERROR]: Invalid selection.")
        except ValueError:
            print("[ERROR]: Invalid input.")

def manage_trip_budget(trip, current_user):
    """Sub-menu for a specific trip's budget and expense records."""
    while True:
        fin = get_trip_financial_summary(trip["trip_id"])
        print("\n" + "=" * 70)
        print(f"      {GREEN}{BOLD}FINANCIAL DASHBOARD: {trip['trip_name'].upper()}{RESET}")
        print("=" * 70)
        print(f"Total Target Budget:     PKR {fin['budget']:,.2f}")
        print(f"Confirmed Bookings:      PKR {fin['bookings_value']:,.2f}")
        print(f"Recorded Out-of-Pocket:  PKR {fin['expenses_value']:,.2f}")
        print("-" * 70)
        print(f"TOTAL COMMITTED:         PKR {fin['total_committed']:,.2f}")
        print(f"REMAINING BUDGET:        PKR {fin['remaining_budget']:,.2f}")
        print(f"EST. COST PER PERSON:    PKR {fin['cost_per_person']:,.2f} ({fin['travellers']} Travellers)")

        # Budget Health Warnings
        if fin["remaining_budget"] < 0:
            print("\n>>> [WARNING]: ESTIMATED EXPENSES EXCEED YOUR TARGET BUDGET! <<<")
        elif fin["remaining_budget"] <= (fin["budget"] * 0.15):
            print("\n>>> [NOTICE]: You have utilized over 85% of your planned budget. <<<")

        print("\nCategory Breakdown:")
        if fin["categories"]:
            for c in fin["categories"]:
                pct = (c["cat_total"] / fin["expenses_value"] * 100) if fin["expenses_value"] > 0 else 0
                print(f"  - {c['expense_category']:<16}: PKR {c['cat_total']:>10,.2f} ({pct:>4.1f}%)")
        else:
            print("  No itemized out-of-pocket expenses logged yet.")

        print("\n" + "-" * 70)
        print("1. Log New Out-of-Pocket Expense")
        print("2. View All Logged Expense Receipts")
        print("3. View Indicative Foreign Currency Conversions")
        print("0. Back to Trips List")
        print("-" * 70)

        ch = input("Select option: ").strip()
        if ch == "1":
            log_new_expense(trip, current_user)
        elif ch == "2":
            view_expense_receipts(trip["trip_id"])
        elif ch == "3":
            display_currency_conversions(fin["total_committed"])
        elif ch == "0":
            break
        else:
            print("[ERROR]: Invalid selection.")

def log_new_expense(trip, current_user):
    """Logs a new out-of-pocket expense in Oracle."""
    print("\nSelect Expense Category:")
    for idx, c in enumerate(EXPENSE_CATEGORIES, 1):
        print(f"  {idx:<2}. {c}")
    try:
        c_sel = int(input("\nCategory (1-12): ").strip()) - 1
        if not (0 <= c_sel < len(EXPENSE_CATEGORIES)):
            print("[ERROR]: Invalid selection.")
            return
        cat = EXPENSE_CATEGORIES[c_sel]

        desc = input("Expense Description: ").strip()
        amt = float(input("Amount in PKR: ").strip())
        method = input("Payment Method (Cash / Credit Card / EasyPaisa / JazzCash): ").strip() or "Cash"

        sql = """
            INSERT INTO TRIP_EXPENSES (
                TRIP_ID, USER_ID, EXPENSE_CATEGORY, DESCRIPTION, 
                AMOUNT_PKR, EXPENSE_DATE, PAYMENT_METHOD, IS_BUDGETED
            ) VALUES (
                :tid, :uid, :cat, :desc, :amt, SYSDATE, :meth, 'YES'
            )
        """
        ok, _, err = execute_non_query(sql, {
            "tid": trip["trip_id"],
            "uid": current_user["user_id"],
            "cat": cat,
            "desc": desc,
            "amt": amt,
            "meth": method
        })
        if ok:
            print(f"\n[SUCCESS]: Recorded PKR {amt:,.2f} under category '{cat}'.")
        else:
            print(f"[ERROR]: Failed to record expense: {err}")
        input("Press Enter to continue...")
    except ValueError:
        print("[ERROR]: Invalid numeric amount.")

def view_expense_receipts(trip_id):
    """Displays itemized expense log."""
    expenses = get_trip_expenses(trip_id)
    print("\n" + "=" * 65)
    print("                 ITEMIZED EXPENSE LOG")
    print("=" * 65)
    if not expenses:
        print("No expenses recorded yet.")
    else:
        print(f"{'DATE':<12} | {'CATEGORY':<14} | {'DESCRIPTION':<22} | {'AMOUNT'}")
        print("-" * 65)
        for e in expenses:
            edate = str(e.get('expense_date') or '').split()[0]
            print(f"{edate:<12} | {e['expense_category']:<14} | {e['description'][:22]:<22} | PKR {e['amount_pkr']:>8,.2f}")
    print("=" * 65)
    input("\nPress Enter to continue...")

def display_currency_conversions(pkr_amount):
    """Displays indicative foreign currency conversions for international tourists."""
    print("\n" + "=" * 65)
    print("      INDICATIVE FOREIGN CURRENCY CONVERSION ESTIMATES")
    print("=" * 65)
    print(f"Base Amount in PKR: PKR {pkr_amount:,.2f}")
    print("Exchange Rates (As of 2026-03-01 Reference Data):")
    print("-" * 65)
    for curr, rate in CURRENCY_RATES_PKR.items():
        converted = pkr_amount / rate
        print(f"  - {curr:<4}: {converted:>10,.2f} {curr:<4} (1 {curr} = {rate:.2f} PKR)")
    print("-" * 65)
    print("Notice: Exchange rates are indicative approximations for international")
    print("budget planning and do not constitute actual banking transactions.")
    print("=" * 65)
    input("\nPress Enter to continue...")
