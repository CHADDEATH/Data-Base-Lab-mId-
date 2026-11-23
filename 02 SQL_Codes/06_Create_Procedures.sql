SET DEFINE OFF;
-- ====================================================================
-- PAK VOYAGE - PAKISTAN TOURISM AND TRAVEL MANAGEMENT AGENCY
-- SCRIPT 06: CREATE STORED PROCEDURES (BUSINESS LOGIC)
-- COMPATIBILITY: Oracle Database 26ai / Oracle SQL Developer
-- ====================================================================

-- 1. USER REGISTRATION PROCEDURE
CREATE OR REPLACE PROCEDURE SP_REGISTER_USER (
    p_full_name       IN  VARCHAR2,
    p_username        IN  VARCHAR2,
    p_age             IN  NUMBER,
    p_country         IN  VARCHAR2,
    p_email           IN  VARCHAR2,
    p_password_hash   IN  VARCHAR2,
    p_user_id         OUT NUMBER,
    p_status_message  OUT VARCHAR2
) AS
    v_user_count  NUMBER;
    v_email_count NUMBER;
BEGIN
    -- Check for duplicate username
    SELECT COUNT(*) INTO v_user_count FROM USERS WHERE LOWER(USERNAME) = LOWER(p_username);
    IF v_user_count > 0 THEN
        p_user_id := -1;
        p_status_message := 'ERROR: Username already exists.';
        RETURN;
    END IF;

    -- Check for duplicate email
    SELECT COUNT(*) INTO v_email_count FROM USERS WHERE LOWER(EMAIL) = LOWER(p_email);
    IF v_email_count > 0 THEN
        p_user_id := -1;
        p_status_message := 'ERROR: Email address already registered.';
        RETURN;
    END IF;

    -- Insert new user
    INSERT INTO USERS (FULL_NAME, USERNAME, AGE, COUNTRY, EMAIL, PASSWORD_HASH, CREATED_AT, STATUS)
    VALUES (p_full_name, p_username, p_age, p_country, p_email, p_password_hash, SYSDATE, 'ACTIVE')
    RETURNING USER_ID INTO p_user_id;

    p_status_message := 'SUCCESS: Tourist account registered successfully.';
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_user_id := -1;
        p_status_message := 'SQL ERROR: ' || SQLERRM;
END SP_REGISTER_USER;
/

-- 2. CREATE NEW TRIP PROCEDURE
CREATE OR REPLACE PROCEDURE SP_CREATE_TRIP (
    p_user_id         IN  NUMBER,
    p_trip_name       IN  VARCHAR2,
    p_start_date      IN  DATE,
    p_end_date        IN  DATE,
    p_num_travellers  IN  NUMBER,
    p_num_adults      IN  NUMBER,
    p_num_children    IN  NUMBER,
    p_budget_pkr      IN  NUMBER,
    p_preferences     IN  VARCHAR2,
    p_description     IN  VARCHAR2,
    p_trip_id         OUT NUMBER,
    p_status_message  OUT VARCHAR2
) AS
BEGIN
    IF p_end_date < p_start_date THEN
        p_trip_id := -1;
        p_status_message := 'ERROR: Trip end date cannot be earlier than start date.';
        RETURN;
    END IF;

    INSERT INTO TRIPS (
        USER_ID, TRIP_NAME, START_DATE, END_DATE, 
        NUM_TRAVELLERS, NUM_ADULTS, NUM_CHILDREN, BUDGET_PKR, 
        TRAVEL_PREFERENCES, TRIP_DESCRIPTION, CREATED_AT, STATUS
    ) VALUES (
        p_user_id, p_trip_name, p_start_date, p_end_date, 
        p_num_travellers, p_num_adults, p_num_children, p_budget_pkr, 
        p_preferences, p_description, SYSDATE, 'PLANNED'
    ) RETURNING TRIP_ID INTO p_trip_id;

    -- Automatically populate basic essential travel checklist
    INSERT INTO TRIP_CHECKLIST (TRIP_ID, ITEM_TITLE, CATEGORY, IS_COMPLETED) VALUES (p_trip_id, 'Original CNIC / Passport AND Identification Documents', 'Documents', 'NO');
    INSERT INTO TRIP_CHECKLIST (TRIP_ID, ITEM_TITLE, CATEGORY, IS_COMPLETED) VALUES (p_trip_id, 'Confirm Hotel AND Transportation Reservations', 'Bookings', 'NO');
    INSERT INTO TRIP_CHECKLIST (TRIP_ID, ITEM_TITLE, CATEGORY, IS_COMPLETED) VALUES (p_trip_id, 'Weather-Appropriate Clothing AND Layers', 'Clothing', 'NO');
    INSERT INTO TRIP_CHECKLIST (TRIP_ID, ITEM_TITLE, CATEGORY, IS_COMPLETED) VALUES (p_trip_id, 'First Aid Kit AND Personal Prescription Medicines', 'Health', 'NO');
    INSERT INTO TRIP_CHECKLIST (TRIP_ID, ITEM_TITLE, CATEGORY, IS_COMPLETED) VALUES (p_trip_id, 'High-Capacity Power Bank AND Charging Cables', 'Electronics', 'NO');
    INSERT INTO TRIP_CHECKLIST (TRIP_ID, ITEM_TITLE, CATEGORY, IS_COMPLETED) VALUES (p_trip_id, 'Cash for Northern Mountain Areas (ATMs are Limited)', 'Finance', 'NO');

    p_status_message := 'SUCCESS: Trip created with default checklist items.';
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_trip_id := -1;
        p_status_message := 'SQL ERROR: ' || SQLERRM;
END SP_CREATE_TRIP;
/

-- 3. CONFIRM BOOKING TRANSACTION PROCEDURE
CREATE OR REPLACE PROCEDURE SP_CONFIRM_BOOKING (
    p_user_id         IN  NUMBER,
    p_trip_id         IN  NUMBER,
    p_service_type    IN  VARCHAR2,
    p_service_ref_id  IN  NUMBER,
    p_travel_date     IN  DATE,
    p_quantity        IN  NUMBER,
    p_unit_price_pkr  IN  NUMBER,
    p_total_cost_pkr  IN  NUMBER,
    p_notes           IN  VARCHAR2,
    p_booking_ref     OUT VARCHAR2,
    p_booking_id      OUT NUMBER,
    p_status_message  OUT VARCHAR2
) AS
    v_seq_val NUMBER;
BEGIN
    -- Generate sequential reference
    SELECT SEQ_BOOKING_NUMBER.NEXTVAL INTO v_seq_val FROM DUAL;
    p_booking_ref := 'PV-BKG-' || TO_CHAR(v_seq_val);

    INSERT INTO BOOKINGS (
        BOOKING_REF, USER_ID, TRIP_ID, SERVICE_TYPE, SERVICE_REF_ID,
        BOOKING_DATE, TRAVEL_DATE, QUANTITY, UNIT_PRICE_PKR, TOTAL_COST_PKR,
        BOOKING_STATUS, PAYMENT_STATUS, NOTES, CREATED_AT
    ) VALUES (
        p_booking_ref, p_user_id, p_trip_id, p_service_type, p_service_ref_id,
        SYSDATE, p_travel_date, p_quantity, p_unit_price_pkr, p_total_cost_pkr,
        'Confirmed', 'Unpaid', p_notes, SYSDATE
    ) RETURNING BOOKING_ID INTO p_booking_id;

    p_status_message := 'SUCCESS: Service booking confirmed under reference ' || p_booking_ref;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_booking_ref := NULL;
        p_booking_id := -1;
        p_status_message := 'SQL ERROR: ' || SQLERRM;
END SP_CONFIRM_BOOKING;
/

-- 4. CANCEL BOOKING PROCEDURE
CREATE OR REPLACE PROCEDURE SP_CANCEL_BOOKING (
    p_booking_id      IN  NUMBER,
    p_user_id         IN  NUMBER,
    p_status_message  OUT VARCHAR2
) AS
    v_curr_status VARCHAR2(20);
BEGIN
    SELECT BOOKING_STATUS INTO v_curr_status 
    FROM BOOKINGS 
    WHERE BOOKING_ID = p_booking_id AND USER_ID = p_user_id;

    IF v_curr_status = 'Cancelled' THEN
        p_status_message := 'INFO: Booking is already cancelled.';
        RETURN;
    END IF;

    UPDATE BOOKINGS 
    SET BOOKING_STATUS = 'Cancelled',
        NOTES = NVL(NOTES, '') || ' [Cancelled by User on ' || TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI') || ']'
    WHERE BOOKING_ID = p_booking_id AND USER_ID = p_user_id;

    p_status_message := 'SUCCESS: Booking reference successfully cancelled.';
    COMMIT;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        p_status_message := 'ERROR: Booking record not found or does not belong to user.';
    WHEN OTHERS THEN
        ROLLBACK;
        p_status_message := 'SQL ERROR: ' || SQLERRM;
END SP_CANCEL_BOOKING;
/

-- 5. RECORD PAYMENT PROCEDURE
CREATE OR REPLACE PROCEDURE SP_RECORD_PAYMENT (
    p_booking_id      IN  NUMBER,
    p_user_id         IN  NUMBER,
    p_amount_pkr      IN  NUMBER,
    p_payment_method  IN  VARCHAR2,
    p_payment_id      OUT NUMBER,
    p_status_message  OUT VARCHAR2
) AS
    v_seq_val NUMBER;
    v_tx_ref  VARCHAR2(50);
BEGIN
    SELECT SEQ_PAYMENT_REF.NEXTVAL INTO v_seq_val FROM DUAL;
    v_tx_ref := 'TXN-PV-' || TO_CHAR(v_seq_val);

    INSERT INTO PAYMENTS (
        BOOKING_ID, USER_ID, AMOUNT_PKR, PAYMENT_DATE, 
        PAYMENT_METHOD, PAYMENT_STATUS, TRANSACTION_REFERENCE
    ) VALUES (
        p_booking_id, p_user_id, p_amount_pkr, SYSDATE, 
        p_payment_method, 'Recorded', v_tx_ref
    ) RETURNING PAYMENT_ID INTO p_payment_id;

    -- Update booking status to Paid
    UPDATE BOOKINGS 
    SET PAYMENT_STATUS = 'Paid' 
    WHERE BOOKING_ID = p_booking_id;

    p_status_message := 'SUCCESS: Payment recorded with transaction ref ' || v_tx_ref;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_payment_id := -1;
        p_status_message := 'SQL ERROR: ' || SQLERRM;
END SP_RECORD_PAYMENT;
/

-- 6. GET USER FINANCIAL SUMMARY PROCEDURE
CREATE OR REPLACE PROCEDURE SP_GET_USER_FINANCIALS (
    p_user_id             IN  NUMBER,
    p_total_trips         OUT NUMBER,
    p_total_bookings_val  OUT NUMBER,
    p_total_paid_val      OUT NUMBER,
    p_total_expenses_val  OUT NUMBER
) AS
BEGIN
    SELECT COUNT(*) INTO p_total_trips 
    FROM TRIPS 
    WHERE USER_ID = p_user_id;

    SELECT NVL(SUM(TOTAL_COST_PKR), 0) INTO p_total_bookings_val 
    FROM BOOKINGS 
    WHERE USER_ID = p_user_id AND BOOKING_STATUS != 'Cancelled';

    SELECT NVL(SUM(AMOUNT_PKR), 0) INTO p_total_paid_val 
    FROM PAYMENTS 
    WHERE USER_ID = p_user_id;

    SELECT NVL(SUM(AMOUNT_PKR), 0) INTO p_total_expenses_val 
    FROM TRIP_EXPENSES 
    WHERE USER_ID = p_user_id;
END SP_GET_USER_FINANCIALS;
/

COMMIT;
