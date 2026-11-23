SET DEFINE OFF;
-- ====================================================================
-- PAK VOYAGE - PAKISTAN TOURISM AND TRAVEL MANAGEMENT AGENCY
-- SCRIPT 10: TEST AND VERIFICATION QUERIES
-- COMPATIBILITY: Oracle Database 26ai / Oracle SQL Developer
-- ====================================================================

-- 1. VERIFY ALL 28 RELATIONAL TABLES EXIST
SELECT table_name 
FROM user_tables 
ORDER BY table_name;

-- 2. VERIFY PRIMARY AND FOREIGN KEY INTEGRITY COUNTS
SELECT 
    constraint_type,
    COUNT(*) AS total_constraints
FROM user_constraints
WHERE constraint_type IN ('P', 'R', 'C', 'U')
GROUP BY constraint_type;

-- 3. TEST STORED PROCEDURE: REGISTER TEST USER
SET SERVEROUTPUT ON;
DECLARE
    v_user_id NUMBER;
    v_msg     VARCHAR2(200);
BEGIN
    SP_REGISTER_USER(
        p_full_name      => 'Ahmed Ali Khan',
        p_username       => 'ahmed_tourist',
        p_age            => 26,
        p_country        => 'Pakistan',
        p_email          => 'ahmed.ali@example.com',
        p_password_hash  => 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        p_user_id        => v_user_id,
        p_status_message => v_msg
    );
    DBMS_OUTPUT.PUT_LINE('Procedure Output: ' || v_msg || ' | User ID: ' || v_user_id);
END;
/

-- 4. TEST STORED PROCEDURE: CREATE A MULTI-DESTINATION TRIP
DECLARE
    v_user_id NUMBER;
    v_trip_id NUMBER;
    v_msg     VARCHAR2(200);
BEGIN
    SELECT USER_ID INTO v_user_id FROM USERS WHERE USERNAME = 'ahmed_tourist';
    
    SP_CREATE_TRIP(
        p_user_id        => v_user_id,
        p_trip_name      => 'Northern Highlights 2026',
        p_start_date     => SYSDATE + 10,
        p_end_date       => SYSDATE + 20,
        p_num_travellers => 3,
        p_num_adults     => 2,
        p_num_children   => 1,
        p_budget_pkr     => 250000.00,
        p_preferences    => 'Hiking, Scenic views, Photography',
        p_description    => 'Family exploration of Islamabad and Skardu valleys',
        p_trip_id        => v_trip_id,
        p_status_message => v_msg
    );
    DBMS_OUTPUT.PUT_LINE('Trip Created: ' || v_msg || ' | Trip ID: ' || v_trip_id);
END;
/

-- 5. TEST STORED PROCEDURE: CONFIRM A HOTEL BOOKING
DECLARE
    v_user_id NUMBER;
    v_trip_id NUMBER;
    v_bkg_ref VARCHAR2(30);
    v_bkg_id  NUMBER;
    v_msg     VARCHAR2(200);
BEGIN
    SELECT USER_ID INTO v_user_id FROM USERS WHERE USERNAME = 'ahmed_tourist';
    SELECT MAX(TRIP_ID) INTO v_trip_id FROM TRIPS WHERE USER_ID = v_user_id;

    SP_CONFIRM_BOOKING(
        p_user_id        => v_user_id,
        p_trip_id        => v_trip_id,
        p_service_type   => 'HOTEL',
        p_service_ref_id => 1, -- Islamabad Serena Hotel
        p_travel_date    => SYSDATE + 10,
        p_quantity       => 1,
        p_unit_price_pkr => 45000.00,
        p_total_cost_pkr => 45000.00,
        p_notes          => 'Academic test hotel booking',
        p_booking_ref    => v_bkg_ref,
        p_booking_id     => v_bkg_id,
        p_status_message => v_msg
    );
    DBMS_OUTPUT.PUT_LINE('Booking Output: ' || v_msg || ' | Ref: ' || v_bkg_ref);
END;
/

-- 6. TEST TRIGGER TRG_PREVENT_DUP_BOOKING
-- Attempting to book the identical hotel on the exact same travel date should raise error -20001
BEGIN
    DBMS_OUTPUT.PUT_LINE('Testing Duplicate Booking Trigger (Expect Error):');
    -- Same user, same service, same travel date
    INSERT INTO BOOKINGS (
        BOOKING_REF, USER_ID, SERVICE_TYPE, SERVICE_REF_ID, 
        BOOKING_DATE, TRAVEL_DATE, QUANTITY, UNIT_PRICE_PKR, 
        TOTAL_COST_PKR, BOOKING_STATUS, PAYMENT_STATUS
    ) VALUES (
        'PV-BKG-TESTDUP', 
        (SELECT USER_ID FROM USERS WHERE USERNAME = 'ahmed_tourist'),
        'HOTEL', 1, SYSDATE, SYSDATE + 10, 1, 45000.00, 45000.00, 'Confirmed', 'Unpaid'
    );
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Caught Expected Trigger Error: ' || SQLERRM);
END;
/

-- 7. TEST VIEW QUERY: VW_USER_TRIP_SUMMARY
SELECT * FROM VW_USER_TRIP_SUMMARY WHERE USERNAME = 'ahmed_tourist';

-- 8. TEST CHECK CONSTRAINT (NEGATIVE PRICE SHOULD FAIL)
BEGIN
    INSERT INTO ACTIVITIES (
        DESTINATION_ID, ACTIVITY_NAME, CATEGORY, LOCATION_ADDRESS, 
        DESCRIPTION, PRICE_PKR, PRICING_MODEL
    ) VALUES (
        1, 'Invalid Price Activity', 'Adventure', 'Test Address', 
        'Test Description', -500.00, 'Per Person'
    );
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Caught Expected Check Constraint Failure: ' || SQLERRM);
END;
/

ROLLBACK;
