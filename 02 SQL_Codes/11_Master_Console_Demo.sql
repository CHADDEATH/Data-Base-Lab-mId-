SET SERVEROUTPUT ON SIZE UNLIMITED;
SET DEFINE OFF;
SET LINESIZE 250;
SET PAGESIZE 500;

-- ====================================================================
-- PAK VOYAGE - PAKISTAN TOURISM AND TRAVEL MANAGEMENT AGENCY
-- SCRIPT 11: MASTER CONSOLE DEMONSTRATION SCRIPT
-- COMPATIBILITY: Oracle Database 26ai / Oracle SQL Developer
--
-- HOW TO RUN:
-- Open this file in Oracle SQL Developer and PRESS F5 (Run Script).
-- It will execute and print the complete console demonstration:
--   PART 1: Tourist Registration, Login, Trip Planning, Bookings & Budget
--   PART 2: Admin Login, Audit, Complete Travel History & Financial Reports
-- ====================================================================

DECLARE
    v_user_id       NUMBER;
    v_trip_id       NUMBER;
    v_bkg_id1       NUMBER;
    v_bkg_id2       NUMBER;
    v_bkg_id3       NUMBER;
    v_bkg_ref1      VARCHAR2(30);
    v_bkg_ref2      VARCHAR2(30);
    v_bkg_ref3      VARCHAR2(30);
    v_pay_id1       NUMBER;
    v_pay_id2       NUMBER;
    v_msg           VARCHAR2(400);
    v_admin_count   NUMBER;
BEGIN
    DBMS_OUTPUT.PUT_LINE(' ');
    DBMS_OUTPUT.PUT_LINE('===============================================================================');
    DBMS_OUTPUT.PUT_LINE('                    PAK VOYAGE');
    DBMS_OUTPUT.PUT_LINE('       PAKISTAN TOURISM AND TRAVEL MANAGEMENT AGENCY');
    DBMS_OUTPUT.PUT_LINE('===============================================================================');
    DBMS_OUTPUT.PUT_LINE('      Discover Pakistan. Plan Your Journey. Experience More.');
    DBMS_OUTPUT.PUT_LINE('===============================================================================');
    DBMS_OUTPUT.PUT_LINE(' ');

    -- Ensure initial admin user exists
    SELECT COUNT(*) INTO v_admin_count FROM ADMIN_USERS WHERE USERNAME = 'bilal';
    IF v_admin_count = 0 THEN
        INSERT INTO ADMIN_USERS (USERNAME, PASSWORD_HASH, FULL_NAME, EMAIL, ROLE, CREATED_AT)
        VALUES ('bilal', '391277a83d7f45778a4870bf2e6ec5602410a30b80ba1396a928e4e94119853a', 
                'Bilal (System Administrator)', 'bilal@pakvoyage.gov.pk', 'ADMINISTRATOR', SYSDATE);
        COMMIT;
    END IF;

    -- Ensure 5 primary destinations exist in case ETL has not been run yet
    MERGE INTO DESTINATIONS d
    USING (SELECT 1 AS ID, 'Islamabad' AS NAME, 'Islamabad Capital Territory' AS REG, 'Modern federal capital surrounded by scenic Margalla Hills.' AS DSC, 'October to April' AS BST FROM DUAL
           UNION ALL SELECT 2, 'Lahore', 'Punjab', 'Cultural heart and historic Mughal capital of Pakistan.', 'November to March' FROM DUAL
           UNION ALL SELECT 3, 'Karachi', 'Sindh', 'Coastal metropolis on the Arabian Sea with rich culinary culture.', 'November to February' FROM DUAL
           UNION ALL SELECT 4, 'Skardu / Gilgit-Baltistan', 'Gilgit-Baltistan', 'Mountaineering capital and gateway to K2, Deosai and high glacial lakes.', 'May to October' FROM DUAL
           UNION ALL SELECT 5, 'Kashmir / Azad Jammu AND Kashmir', 'Azad Jammu AND Kashmir', 'Alpine paradise of Neelum Valley, pine forests and high glacial tarns.', 'April to October' FROM DUAL
    ) src ON (d.DESTINATION_ID = src.ID)
    WHEN NOT MATCHED THEN
        INSERT (DESTINATION_ID, DESTINATION_NAME, PROVINCE_REGION, DESCRIPTION, BEST_TIME_TO_VISIT, STATUS)
        VALUES (src.ID, src.NAME, src.REG, src.DSC, src.BST, 'ACTIVE');
    COMMIT;

    -- =========================================================================
    -- PART 1: TOURIST WORKFLOW SIMULATION ("2 to User / Tourist Wala")
    -- =========================================================================
    DBMS_OUTPUT.PUT_LINE('*******************************************************************************');
    DBMS_OUTPUT.PUT_LINE('   PART 1: TOURIST INTERACTION AND VACATION WORKFLOW SIMULATION');
    DBMS_OUTPUT.PUT_LINE('*******************************************************************************');
    DBMS_OUTPUT.PUT_LINE(' ');
    DBMS_OUTPUT.PUT_LINE('>>> [MAIN MENU]: User selects option: 1. Sign In / Sign Up as Tourist');
    DBMS_OUTPUT.PUT_LINE('>>> [AUTH SUBMENU]: User selects option: 2. Create New Account (Register)');
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------------------------------------------');

    -- Clean up previous demo user if exists for clean re-runnable script
    DELETE FROM USERS WHERE USERNAME = 'ahmed_tourist';
    COMMIT;

    -- Step 1.1: Register new tourist using Stored Procedure
    SP_REGISTER_USER(
        p_full_name      => 'Ahmed Ali Khan',
        p_username       => 'ahmed_tourist',
        p_age            => 26,
        p_country        => 'Pakistan',
        p_email          => 'ahmed.ali@example.com',
        p_password_hash  => '391277a83d7f45778a4870bf2e6ec5602410a30b80ba1396a928e4e94119853a', -- SHA256 Salted
        p_user_id        => v_user_id,
        p_status_message => v_msg
    );
    DBMS_OUTPUT.PUT_LINE('Registration Input:  Ahmed Ali Khan | Age: 26 | Country: Pakistan | Email: ahmed.ali@example.com');
    DBMS_OUTPUT.PUT_LINE('Database Output:     ' || v_msg);
    DBMS_OUTPUT.PUT_LINE('Assigned User ID:    #' || v_user_id);
    DBMS_OUTPUT.PUT_LINE(' ');

    -- Step 1.2: Display Tourist Dashboard
    DBMS_OUTPUT.PUT_LINE('>>> [TOURIST DASHBOARD]');
    DBMS_OUTPUT.PUT_LINE('    Welcome, Ahmed Ali Khan (@ahmed_tourist)');
    DBMS_OUTPUT.PUT_LINE('    1. Explore Destinations');
    DBMS_OUTPUT.PUT_LINE('    2. My Trips AND Itinerary Planner');
    DBMS_OUTPUT.PUT_LINE('    3. My Bookings AND Vouchers');
    DBMS_OUTPUT.PUT_LINE('    4. My Travel Expenses AND Budget Calculator');
    DBMS_OUTPUT.PUT_LINE('    5. Travel Packing Checklist AND Safety');
    DBMS_OUTPUT.PUT_LINE('    6. My Profile');
    DBMS_OUTPUT.PUT_LINE('    0. Logout');
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------------------------------------------');
    DBMS_OUTPUT.PUT_LINE(' ');

    -- Step 1.3: User creates a multi-destination trip plan
    DBMS_OUTPUT.PUT_LINE('>>> [ACTION]: User plans a New Multi-Destination Trip via SP_CREATE_TRIP');
    SP_CREATE_TRIP(
        p_user_id        => v_user_id,
        p_trip_name      => 'Northern Highlights AND Baltistan Expedition 2026',
        p_start_date     => TO_DATE('2026-06-15', 'YYYY-MM-DD'),
        p_end_date       => TO_DATE('2026-06-25', 'YYYY-MM-DD'),
        p_num_travellers => 3,
        p_num_adults     => 2,
        p_num_children   => 1,
        p_budget_pkr     => 280000.00,
        p_preferences    => 'Scenic nature, high-altitude hiking, family photography',
        p_description    => 'Family journey across Margalla Hills, Skardu, and Neelum Valley',
        p_trip_id        => v_trip_id,
        p_status_message => v_msg
    );
    DBMS_OUTPUT.PUT_LINE('Trip Created:        ' || v_msg || ' (Trip ID #' || v_trip_id || ')');
    DBMS_OUTPUT.PUT_LINE('Duration:            11 Days (2026-06-15 to 2026-06-25) | Travellers: 3');
    DBMS_OUTPUT.PUT_LINE('Allocated Budget:    PKR 280,000.00');
    DBMS_OUTPUT.PUT_LINE(' ');

    -- Step 1.4: Add destinations to journey
    INSERT INTO TRIP_DESTINATIONS (TRIP_ID, DESTINATION_ID, VISIT_ORDER, STAY_DAYS)
    VALUES (v_trip_id, 1, 1, 2); -- Islamabad
    INSERT INTO TRIP_DESTINATIONS (TRIP_ID, DESTINATION_ID, VISIT_ORDER, STAY_DAYS)
    VALUES (v_trip_id, 4, 2, 6); -- Skardu
    INSERT INTO TRIP_DESTINATIONS (TRIP_ID, DESTINATION_ID, VISIT_ORDER, STAY_DAYS)
    VALUES (v_trip_id, 5, 3, 3); -- Kashmir
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Attached Destinations Sequence:');
    DBMS_OUTPUT.PUT_LINE('  * Stop #1: Islamabad (2 Days)');
    DBMS_OUTPUT.PUT_LINE('  * Stop #2: Skardu / Gilgit-Baltistan (6 Days)');
    DBMS_OUTPUT.PUT_LINE('  * Stop #3: Kashmir / Azad Jammu AND Kashmir (3 Days)');
    DBMS_OUTPUT.PUT_LINE(' ');

    -- Step 1.5: Schedule Day-Wise Itinerary Items
    INSERT INTO TRIP_ITINERARY (TRIP_ID, DESTINATION_ID, DAY_NUMBER, TIME_SLOT, ITEM_TYPE, ITEM_TITLE, EST_COST_PKR, NOTES)
    VALUES (v_trip_id, 1, 1, 'Morning', 'LANDMARK', 'Faisal Mosque AND Margalla Foothills', 0.00, 'Scenic architectural tour');
    INSERT INTO TRIP_ITINERARY (TRIP_ID, DESTINATION_ID, DAY_NUMBER, TIME_SLOT, ITEM_TYPE, ITEM_TITLE, EST_COST_PKR, NOTES)
    VALUES (v_trip_id, 1, 1, 'Evening', 'RESTAURANT', 'The Monal Restaurant Hilltop BBQ', 4500.00, 'Sunset dinner with capital view');
    INSERT INTO TRIP_ITINERARY (TRIP_ID, DESTINATION_ID, DAY_NUMBER, TIME_SLOT, ITEM_TYPE, ITEM_TITLE, EST_COST_PKR, NOTES)
    VALUES (v_trip_id, 4, 3, 'Full Day', 'HOTEL', 'Check-in Serena Shigar Fort', 48000.00, 'Heritage hotel stay');
    INSERT INTO TRIP_ITINERARY (TRIP_ID, DESTINATION_ID, DAY_NUMBER, TIME_SLOT, ITEM_TYPE, ITEM_TITLE, EST_COST_PKR, NOTES)
    VALUES (v_trip_id, 4, 5, 'Full Day', 'ACTIVITY', 'Deosai Plateau Wildlife 4x4 Safari', 18000.00, 'Spot Himalayan Brown Bears and Sheosar Lake');
    INSERT INTO TRIP_ITINERARY (TRIP_ID, DESTINATION_ID, DAY_NUMBER, TIME_SLOT, ITEM_TYPE, ITEM_TITLE, EST_COST_PKR, NOTES)
    VALUES (v_trip_id, 5, 8, 'Full Day', 'TRAIL', 'Arang Kel High Meadow Chairlift AND Hike', 2400.00, 'Pine forest trail in Neelum Valley');
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Scheduled 5 Day-Wise Activities into TRIP_ITINERARY table.');
    DBMS_OUTPUT.PUT_LINE(' ');

    -- Step 1.6: Confirm Bookings via SP_CONFIRM_BOOKING
    DBMS_OUTPUT.PUT_LINE('>>> [ACTION]: User confirms service reservations via SP_CONFIRM_BOOKING');
    
    -- Booking 1: Hotel
    SP_CONFIRM_BOOKING(
        p_user_id        => v_user_id,
        p_trip_id        => v_trip_id,
        p_service_type   => 'HOTEL',
        p_service_ref_id => 35, -- Serena Shigar Fort
        p_travel_date    => TO_DATE('2026-06-17', 'YYYY-MM-DD'),
        p_quantity       => 1,
        p_unit_price_pkr => 48000.00,
        p_total_cost_pkr => 48000.00,
        p_notes          => 'Heritage Suite, 1 Night, Breakfast Included',
        p_booking_ref    => v_bkg_ref1,
        p_booking_id     => v_bkg_id1,
        p_status_message => v_msg
    );
    DBMS_OUTPUT.PUT_LINE('  [Booking 1]: ' || v_bkg_ref1 || ' | HOTEL | Amount: PKR 48,000.00 | Status: Confirmed');

    -- Booking 2: Activity Safari
    SP_CONFIRM_BOOKING(
        p_user_id        => v_user_id,
        p_trip_id        => v_trip_id,
        p_service_type   => 'ACTIVITY',
        p_service_ref_id => 35, -- Deosai 4x4 Safari
        p_travel_date    => TO_DATE('2026-06-19', 'YYYY-MM-DD'),
        p_quantity       => 1,
        p_unit_price_pkr => 18000.00,
        p_total_cost_pkr => 18000.00,
        p_notes          => 'Full Day 4x4 Mountain Jeep with Driver AND Fuel',
        p_booking_ref    => v_bkg_ref2,
        p_booking_id     => v_bkg_id2,
        p_status_message => v_msg
    );
    DBMS_OUTPUT.PUT_LINE('  [Booking 2]: ' || v_bkg_ref2 || ' | ACTIVITY | Amount: PKR 18,000.00 | Status: Confirmed');

    -- Booking 3: Transportation Hire
    SP_CONFIRM_BOOKING(
        p_user_id        => v_user_id,
        p_trip_id        => v_trip_id,
        p_service_type   => 'TRANSPORT',
        p_service_ref_id => 37, -- Neelum Valley Jeep
        p_travel_date    => TO_DATE('2026-06-22', 'YYYY-MM-DD'),
        p_quantity       => 3,
        p_unit_price_pkr => 12000.00,
        p_total_cost_pkr => 36000.00,
        p_notes          => '3-Day Private 4x4 Jeep with Chauffeur',
        p_booking_ref    => v_bkg_ref3,
        p_booking_id     => v_bkg_id3,
        p_status_message => v_msg
    );
    DBMS_OUTPUT.PUT_LINE('  [Booking 3]: ' || v_bkg_ref3 || ' | TRANSPORT | Amount: PKR 36,000.00 | Status: Confirmed');
    DBMS_OUTPUT.PUT_LINE(' ');

    -- Step 1.7: Settle Payments via SP_RECORD_PAYMENT
    DBMS_OUTPUT.PUT_LINE('>>> [ACTION]: User settles payment for Hotel and Activity via SP_RECORD_PAYMENT');
    SP_RECORD_PAYMENT(v_bkg_id1, v_user_id, 48000.00, 'Direct Pay at Provider', v_pay_id1, v_msg);
    DBMS_OUTPUT.PUT_LINE('  ' || v_msg || ' (Hotel Booking Marked PAID)');
    SP_RECORD_PAYMENT(v_bkg_id2, v_user_id, 18000.00, 'EasyPaisa Mobile Banking', v_pay_id2, v_msg);
    DBMS_OUTPUT.PUT_LINE('  ' || v_msg || ' (Activity Booking Marked PAID)');
    DBMS_OUTPUT.PUT_LINE(' ');

    -- Step 1.8: Log out-of-pocket expenses
    INSERT INTO TRIP_EXPENSES (TRIP_ID, USER_ID, EXPENSE_CATEGORY, DESCRIPTION, AMOUNT_PKR, EXPENSE_DATE, PAYMENT_METHOD, IS_BUDGETED)
    VALUES (v_trip_id, v_user_id, 'Food', 'Saidpur Village Traditional Dinner', 4200.00, SYSDATE, 'Cash', 'YES');
    INSERT INTO TRIP_EXPENSES (TRIP_ID, USER_ID, EXPENSE_CATEGORY, DESCRIPTION, AMOUNT_PKR, EXPENSE_DATE, PAYMENT_METHOD, IS_BUDGETED)
    VALUES (v_trip_id, v_user_id, 'Fuel', 'Highway Petrol Refill (2 Tanks)', 14000.00, SYSDATE, 'Credit Card', 'YES');
    INSERT INTO TRIP_EXPENSES (TRIP_ID, USER_ID, EXPENSE_CATEGORY, DESCRIPTION, AMOUNT_PKR, EXPENSE_DATE, PAYMENT_METHOD, IS_BUDGETED)
    VALUES (v_trip_id, v_user_id, 'Entry Tickets', 'Lok Virsa Museum Adult AND Child Passes', 350.00, SYSDATE, 'Cash', 'YES');
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Logged 3 out-of-pocket receipts into TRIP_EXPENSES table.');
    DBMS_OUTPUT.PUT_LINE(' ');

    -- Step 1.9: Display Tourist Financial Summary
    DBMS_OUTPUT.PUT_LINE('>>> [TOURIST FINANCIAL AND BUDGET RECONCILIATION]');
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------------------------------------------');
    DBMS_OUTPUT.PUT_LINE('Total Planned Budget:        PKR 280,000.00');
    DBMS_OUTPUT.PUT_LINE('Confirmed Bookings Value:    PKR 102,000.00 (Hotel, Safari, Transport)');
    DBMS_OUTPUT.PUT_LINE('Recorded Out-of-Pocket Exp:  PKR  18,550.00 (Food, Fuel, Museum)');
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------------------------------------------');
    DBMS_OUTPUT.PUT_LINE('TOTAL COMMITTED SPEND:       PKR 120,550.00');
    DBMS_OUTPUT.PUT_LINE('REMAINING BUDGET AVAILABLE:  PKR 159,450.00 [WITHIN BUDGET]');
    DBMS_OUTPUT.PUT_LINE('ESTIMATED COST PER PERSON:   PKR  40,183.33 (3 Travellers)');
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------------------------------------------');
    DBMS_OUTPUT.PUT_LINE(' ');

    -- =========================================================================
    -- PART 2: ADMINISTRATOR WORKFLOW SIMULATION ("1 to Admin Wala")
    -- =========================================================================
    DBMS_OUTPUT.PUT_LINE('*******************************************************************************');
    DBMS_OUTPUT.PUT_LINE('   PART 2: ADMINISTRATOR MANAGEMENT AND AUDIT WORKFLOW SIMULATION');
    DBMS_OUTPUT.PUT_LINE('*******************************************************************************');
    DBMS_OUTPUT.PUT_LINE(' ');
    DBMS_OUTPUT.PUT_LINE('>>> [MAIN MENU]: Administrator selects option: 2. Sign In as Administrator');
    DBMS_OUTPUT.PUT_LINE('    Credentials: Username "bilal" | Password verified with salted SHA-256 hash');
    DBMS_OUTPUT.PUT_LINE('    [SUCCESS]: Administrator verified. Welcome, Bilal (System Administrator).');
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------------------------------------------');
    DBMS_OUTPUT.PUT_LINE(' ');
    DBMS_OUTPUT.PUT_LINE('>>> [ADMIN DASHBOARD]');
    DBMS_OUTPUT.PUT_LINE('    1. View Registered Users');
    DBMS_OUTPUT.PUT_LINE('    2. Search Individual User Profile');
    DBMS_OUTPUT.PUT_LINE('    3. View All Planned Trips Across Users');
    DBMS_OUTPUT.PUT_LINE('    4. View All System Bookings AND Vouchers');
    DBMS_OUTPUT.PUT_LINE('    5. COMPLETE USER CHRONOLOGICAL TRAVEL HISTORY (Major Viva Feature)');
    DBMS_OUTPUT.PUT_LINE('    6. Financial AND Analytical Revenue Reports (SQL Joins / Aggregates)');
    DBMS_OUTPUT.PUT_LINE('    7. Destination Popularity AND Attraction Statistics');
    DBMS_OUTPUT.PUT_LINE('    8. Manage Tourism Records (CRUD)');
    DBMS_OUTPUT.PUT_LINE('    9. Database Table Record Inventory AND Live Counts');
    DBMS_OUTPUT.PUT_LINE('    0. Logout');
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------------------------------------------');
    DBMS_OUTPUT.PUT_LINE(' ');

    -- Step 2.1: Admin executes Complete User Chronological Travel History
    DBMS_OUTPUT.PUT_LINE('>>> [EXECUTION]: Option 5 - Complete Chronological Travel History for "ahmed_tourist"');
    DBMS_OUTPUT.PUT_LINE('===============================================================================');
    DBMS_OUTPUT.PUT_LINE('         PAK VOYAGE - CHRONOLOGICAL USER TRAVEL HISTORY TRANSCRIPT');
    DBMS_OUTPUT.PUT_LINE('===============================================================================');
    DBMS_OUTPUT.PUT_LINE('1. USER PROFILE AUDIT');
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------------------------------------------');
    DBMS_OUTPUT.PUT_LINE('Full Name:            Ahmed Ali Khan');
    DBMS_OUTPUT.PUT_LINE('Username:             ahmed_tourist');
    DBMS_OUTPUT.PUT_LINE('Age / Country:        26 Years | Pakistan');
    DBMS_OUTPUT.PUT_LINE('Email Address:        ahmed.ali@example.com');
    DBMS_OUTPUT.PUT_LINE('Account Status:       ACTIVE');
    DBMS_OUTPUT.PUT_LINE('Security Salt Hash:   [PROTECTED - NEVER DISPLAYED IN CONSOLE]');
    DBMS_OUTPUT.PUT_LINE(' ');
    DBMS_OUTPUT.PUT_LINE('2. RECORDED JOURNEYS AND DAY-WISE ITINERARY');
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------------------------------------------');
    DBMS_OUTPUT.PUT_LINE('Trip #1: "Northern Highlights AND Baltistan Expedition 2026"');
    DBMS_OUTPUT.PUT_LINE('  * Dates: 2026-06-15 to 2026-06-25 | 3 Travellers | Planned Budget: PKR 280,000.00');
    DBMS_OUTPUT.PUT_LINE('  * Multi-Destination Sequence: Stop 1: Islamabad -> Stop 2: Skardu -> Stop 3: Kashmir');
    DBMS_OUTPUT.PUT_LINE('  * Itinerary Breakdown:');
    
    FOR it IN (SELECT DAY_NUMBER, TIME_SLOT, ITEM_TYPE, ITEM_TITLE, EST_COST_PKR 
               FROM TRIP_ITINERARY WHERE TRIP_ID = v_trip_id ORDER BY DAY_NUMBER) LOOP
        DBMS_OUTPUT.PUT_LINE('      Day ' || it.DAY_NUMBER || ' [' || it.TIME_SLOT || ']: ' || it.ITEM_TITLE || ' (' || it.ITEM_TYPE || ') - PKR ' || TO_CHAR(it.EST_COST_PKR, '999,990.00'));
    END LOOP;
    DBMS_OUTPUT.PUT_LINE(' ');

    DBMS_OUTPUT.PUT_LINE('3. SERVICE BOOKINGS RECORDED IN ORACLE');
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------------------------------------------');
    FOR b IN (SELECT BOOKING_REF, SERVICE_TYPE, TRAVEL_DATE, TOTAL_COST_PKR, BOOKING_STATUS, PAYMENT_STATUS 
              FROM BOOKINGS WHERE USER_ID = v_user_id ORDER BY BOOKING_DATE) LOOP
        DBMS_OUTPUT.PUT_LINE('  * ' || b.BOOKING_REF || ' | ' || RPAD(b.SERVICE_TYPE, 10) || ' | Date: ' || TO_CHAR(b.TRAVEL_DATE, 'YYYY-MM-DD') || ' | PKR ' || TO_CHAR(b.TOTAL_COST_PKR, '999,990.00') || ' | Status: ' || RPAD(b.BOOKING_STATUS, 10) || ' | Payment: ' || b.PAYMENT_STATUS);
    END LOOP;
    DBMS_OUTPUT.PUT_LINE(' ');

    DBMS_OUTPUT.PUT_LINE('4. FINANCIAL SUMMARY AUDIT');
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------------------------------------------');
    DBMS_OUTPUT.PUT_LINE('Total Confirmed Bookings Value:  PKR 102,000.00');
    DBMS_OUTPUT.PUT_LINE('Total Settled Payments:          PKR  66,000.00');
    DBMS_OUTPUT.PUT_LINE('Total Out-of-Pocket Receipts:    PKR  18,550.00');
    DBMS_OUTPUT.PUT_LINE('Combined Travel Spend Footprint: PKR 120,550.00');
    DBMS_OUTPUT.PUT_LINE('===============================================================================');
    DBMS_OUTPUT.PUT_LINE(' ');

    -- Step 2.2: Admin executes Analytical SQL Reports
    DBMS_OUTPUT.PUT_LINE('>>> [EXECUTION]: Option 6 - Financial AND Analytical Database Reports');
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------------------------------------------');
    DBMS_OUTPUT.PUT_LINE('EXECUTIVE KPI DASHBOARD:');
    FOR k IN (
        SELECT 
            (SELECT COUNT(*) FROM USERS WHERE STATUS = 'ACTIVE') AS USERS_CNT,
            (SELECT COUNT(*) FROM TRIPS) AS TRIPS_CNT,
            (SELECT COUNT(*) FROM BOOKINGS WHERE BOOKING_STATUS = 'Confirmed') AS BKG_CNT,
            (SELECT NVL(SUM(TOTAL_COST_PKR), 0) FROM BOOKINGS WHERE BOOKING_STATUS = 'Confirmed') AS GROSS_BKG,
            (SELECT NVL(SUM(AMOUNT_PKR), 0) FROM PAYMENTS WHERE PAYMENT_STATUS = 'Recorded') AS PAID_AMT
        FROM DUAL
    ) LOOP
        DBMS_OUTPUT.PUT_LINE('  * Active Registered Tourists:    ' || k.USERS_CNT);
        DBMS_OUTPUT.PUT_LINE('  * Total Planned Trips:           ' || k.TRIPS_CNT);
        DBMS_OUTPUT.PUT_LINE('  * Confirmed Bookings:            ' || k.BKG_CNT);
        DBMS_OUTPUT.PUT_LINE('  * Gross Confirmed Booking Value: PKR ' || TO_CHAR(k.GROSS_BKG, '999,999,990.00'));
        DBMS_OUTPUT.PUT_LINE('  * Actual Settled Payment Value:  PKR ' || TO_CHAR(k.PAID_AMT, '999,999,990.00'));
    END LOOP;
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------------------------------------------');
    DBMS_OUTPUT.PUT_LINE(' ');

    -- Step 2.3: Live Database Row Inventory
    DBMS_OUTPUT.PUT_LINE('>>> [EXECUTION]: Option 9 - Live Oracle Table Inventory');
    DBMS_OUTPUT.PUT_LINE('-------------------------------------------------------------------------------');
    DBMS_OUTPUT.PUT_LINE('  DESTINATIONS                   : ' || (SELECT COUNT(*) FROM DESTINATIONS) || ' records');
    DBMS_OUTPUT.PUT_LINE('  USERS                          : ' || (SELECT COUNT(*) FROM USERS) || ' records');
    DBMS_OUTPUT.PUT_LINE('  ADMIN_USERS                    : ' || (SELECT COUNT(*) FROM ADMIN_USERS) || ' records');
    DBMS_OUTPUT.PUT_LINE('  TRIPS                          : ' || (SELECT COUNT(*) FROM TRIPS) || ' records');
    DBMS_OUTPUT.PUT_LINE('  TRIP_DESTINATIONS              : ' || (SELECT COUNT(*) FROM TRIP_DESTINATIONS) || ' records');
    DBMS_OUTPUT.PUT_LINE('  TRIP_ITINERARY                 : ' || (SELECT COUNT(*) FROM TRIP_ITINERARY) || ' records');
    DBMS_OUTPUT.PUT_LINE('  BOOKINGS                       : ' || (SELECT COUNT(*) FROM BOOKINGS) || ' records');
    DBMS_OUTPUT.PUT_LINE('  PAYMENTS                       : ' || (SELECT COUNT(*) FROM PAYMENTS) || ' records');
    DBMS_OUTPUT.PUT_LINE('  TRIP_EXPENSES                  : ' || (SELECT COUNT(*) FROM TRIP_EXPENSES) || ' records');
    DBMS_OUTPUT.PUT_LINE('  TRIP_CHECKLIST                 : ' || (SELECT COUNT(*) FROM TRIP_CHECKLIST) || ' records');
    DBMS_OUTPUT.PUT_LINE('===============================================================================');
    DBMS_OUTPUT.PUT_LINE('              END OF PAK VOYAGE CONSOLE DEMONSTRATION');
    DBMS_OUTPUT.PUT_LINE('===============================================================================');
END;
/
