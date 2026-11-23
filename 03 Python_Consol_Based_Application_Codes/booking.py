"""
Pak Voyage - Centralized Booking Management Module
Transactional creation, reference generation, persistence in Oracle, and status tracking.
"""

from database import execute_query, execute_non_query, execute_insert_returning_id

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

def create_booking_record(user_id, trip_id, service_type, service_ref_id, travel_date, quantity, unit_price_pkr, total_cost_pkr, notes=""):
    """
    Creates an academic booking record in Oracle.
    Prevents duplicate active booking on the exact same date.
    """
    # 1. Duplicate check
    dup_sql = """
        SELECT BOOKING_ID FROM BOOKINGS 
        WHERE USER_ID = :uid AND SERVICE_TYPE = :st AND SERVICE_REF_ID = :sref 
          AND TRUNC(TRAVEL_DATE) = TO_DATE(:tdate, 'YYYY-MM-DD')
          AND BOOKING_STATUS IN ('Confirmed', 'Pending')
    """
    try:
        existing = execute_query(dup_sql, {
            "uid": user_id,
            "st": service_type,
            "sref": service_ref_id,
            "tdate": travel_date
        })
        if existing:
            return False, None, "You already have an active booking for this service on the chosen date."
    except Exception:
        pass  # If date format fails, insert statement will catch constraint

    # 2. Generate unique reference using sequence
    seq_sql = "SELECT SEQ_BOOKING_NUMBER.NEXTVAL AS SEQ FROM DUAL"
    seq_res = execute_query(seq_sql)
    if seq_res and seq_res[0].get("seq"):
        seq_num = seq_res[0]["seq"]
    else:
        # Fallback if sequence not yet created in dev
        import time
        seq_num = int(time.time()) % 100000

    booking_ref = f"PV-BKG-{seq_num}"

    # 3. Insert into BOOKINGS table
    insert_sql = """
        INSERT INTO BOOKINGS (
            BOOKING_REF, USER_ID, TRIP_ID, SERVICE_TYPE, SERVICE_REF_ID,
            BOOKING_DATE, TRAVEL_DATE, QUANTITY, UNIT_PRICE_PKR, TOTAL_COST_PKR,
            BOOKING_STATUS, PAYMENT_STATUS, NOTES, CREATED_AT
        ) VALUES (
            :bref, :uid, :tid, :stype, :sref,
            SYSDATE, TO_DATE(:tdate, 'YYYY-MM-DD'), :qty, :uprice, :totcost,
            'Confirmed', 'Unpaid', :notes, SYSDATE
        ) RETURNING BOOKING_ID INTO :out_id
    """
    params = {
        "bref": booking_ref,
        "uid": user_id,
        "tid": trip_id,
        "stype": service_type,
        "sref": service_ref_id,
        "tdate": travel_date,
        "qty": quantity,
        "uprice": unit_price_pkr,
        "totcost": total_cost_pkr,
        "notes": notes
    }

    new_id, err = execute_insert_returning_id(insert_sql, params)
    if err:
        return False, None, f"Database transaction failed: {err}"

    return True, booking_ref, f"Booking successfully confirmed in Oracle Database."

def get_user_bookings(user_id):
    """Retrieves all bookings made by a user."""
    sql = """
        SELECT b.*, t.TRIP_NAME
        FROM BOOKINGS b
        LEFT JOIN TRIPS t ON b.TRIP_ID = t.TRIP_ID
        WHERE b.USER_ID = :uid
        ORDER BY b.BOOKING_DATE DESC
    """
    return execute_query(sql, {"uid": user_id})

def cancel_user_booking(booking_id, user_id):
    """Updates booking status to 'Cancelled' without deleting history."""
    check_sql = "SELECT BOOKING_STATUS FROM BOOKINGS WHERE BOOKING_ID = :bid AND USER_ID = :uid"
    res = execute_query(check_sql, {"bid": booking_id, "uid": user_id})
    if not res:
        return False, "Booking not found or does not belong to you."

    if res[0]["booking_status"] == "Cancelled":
        return False, "This booking has already been cancelled."

    cancel_sql = """
        UPDATE BOOKINGS 
        SET BOOKING_STATUS = 'Cancelled',
            NOTES = NVL(NOTES, '') || ' [Cancelled on ' || TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI') || ']'
        WHERE BOOKING_ID = :bid AND USER_ID = :uid
    """
    ok, _, err = execute_non_query(cancel_sql, {"bid": booking_id, "uid": user_id})
    if ok:
        return True, "Booking reference successfully cancelled."
    return False, f"Failed to cancel booking: {err}"

def display_my_bookings(current_user):
    """Interactive screen showing tourist's active and past bookings."""
    while True:
        bookings = get_user_bookings(current_user["user_id"])
        print("\n" + "=" * 70)
        print(f"      {GREEN}{BOLD}MY BOOKINGS & RESERVATIONS - {current_user['full_name'].upper()}{RESET}")
        print("=" * 70)

        if not bookings:
            print("No bookings found in your travel account.")
            print("-" * 70)
            input("Press Enter to return...")
            break

        print(f"{'#':<3} | {'REF':<15} | {'TYPE':<10} | {'DATE':<12} | {'TOTAL':<12} | {'STATUS':<10} | {'PAYMENT'}")
        print("-" * 70)
        for idx, b in enumerate(bookings, 1):
            tdate = str(b.get('travel_date') or '').split()[0]
            print(f"{idx:<3} | {b['booking_ref']:<15} | {b['service_type']:<10} | {tdate:<12} | PKR {b['total_cost_pkr']:<8,.0f} | {b['booking_status']:<10} | {b['payment_status']}")
        print("-" * 70)
        print("1. View Full Booking Voucher Details")
        print("2. Cancel a Booking")
        print("0. Back to Tourist Dashboard")

        choice = input("\nSelect option: ").strip()
        if choice == "1":
            try:
                b_sel = int(input("Enter Booking Number: ").strip()) - 1
                if 0 <= b_sel < len(bookings):
                    b = bookings[b_sel]
                    print("\n" + "=" * 65)
                    print(f"      OFFICIAL ACADEMIC BOOKING VOUCHER")
                    print("=" * 65)
                    print(f"Booking Reference:    {b['booking_ref']}")
                    print(f"Customer Name:        {current_user['full_name']} ({current_user['email']})")
                    print(f"Trip Association:     {b.get('trip_name') or 'Standalone Booking'}")
                    print(f"Service Type:         {b['service_type']}")
                    print(f"Travel Date:          {str(b.get('travel_date') or '').split()[0]}")
                    print(f"Quantity:             {b['quantity']}")
                    print(f"Unit Rate:            PKR {b['unit_price_pkr']:,.2f}")
                    print(f"Total Amount:         PKR {b['total_cost_pkr']:,.2f}")
                    print(f"Booking Status:       {b['booking_status']}")
                    print(f"Payment Status:       {b['payment_status']}")
                    print(f"Notes / Add-ons:      {b.get('notes') or 'None'}")
                    print("=" * 65)
                    input("\nPress Enter to continue...")
                else:
                    print("[ERROR]: Invalid number.")
            except ValueError:
                print("[ERROR]: Invalid input.")
        elif choice == "2":
            try:
                b_sel = int(input("Enter Booking Number to cancel: ").strip()) - 1
                if 0 <= b_sel < len(bookings):
                    b = bookings[b_sel]
                    confirm = input(f"Are you sure you want to cancel booking {b['booking_ref']}? (y/n): ").strip().lower()
                    if confirm == "y":
                        ok, msg = cancel_user_booking(b["booking_id"], current_user["user_id"])
                        print(f"\n{msg}")
                        input("Press Enter to continue...")
                else:
                    print("[ERROR]: Invalid number.")
            except ValueError:
                print("[ERROR]: Invalid input.")
        elif choice == "0":
            break
        else:
            print("[ERROR]: Invalid option.")
