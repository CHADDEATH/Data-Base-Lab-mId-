SET DEFINE OFF;
-- ====================================================================
-- PAK VOYAGE - PAKISTAN TOURISM AND TRAVEL MANAGEMENT AGENCY
-- SCRIPT 04: CREATE SEQUENCES
-- COMPATIBILITY: Oracle Database 26ai / Oracle SQL Developer
-- ====================================================================

-- Drop existing sequences if recreating
BEGIN
    FOR s IN (SELECT sequence_name FROM user_sequences WHERE sequence_name IN (
        'SEQ_BOOKING_NUMBER', 'SEQ_PAYMENT_REF', 'SEQ_EXPENSE_REF', 'SEQ_TRIP_REF'
    )) LOOP
        EXECUTE IMMEDIATE 'DROP SEQUENCE ' || s.sequence_name;
    END LOOP;
END;
/

-- Sequence for human-readable booking reference generation (e.g. PV-BKG-10001)
CREATE SEQUENCE SEQ_BOOKING_NUMBER
    START WITH 10001
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

-- Sequence for payment reference transaction numbers
CREATE SEQUENCE SEQ_PAYMENT_REF
    START WITH 50001
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

-- Sequence for expense tracking references
CREATE SEQUENCE SEQ_EXPENSE_REF
    START WITH 80001
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

-- Sequence for custom trip plan codes
CREATE SEQUENCE SEQ_TRIP_REF
    START WITH 20001
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

COMMIT;
