# Pak Voyage – Pakistan Tourism & Travel Management System
**BS Computer Science — Database Management Systems (DBMS) Lab Final Project**  
**Semester:** Fall 2026  
**Course Instructor:** Ma'am Tayyaba Shehzad  
**Submitted By:** Bilal Tahir 42776
                  Roman Saadat 42792

---

## 1. Project Overview

**Pak Voyage** is a database-driven console application developed for the DBMS Lab Final Project. The system models a realistic tourism and travel management agency for Pakistan, connecting a Python 3 console application directly to an **Oracle Database 26ai** backend using `python-oracledb` (Thin Mode).

The project is populated with **1,270 verified, real-world tourism records** across five major travel destinations in Pakistan:
1. **Islamabad Capital Territory** (Margalla trails, monuments, viewpoints, family parks)
2. **Lahore (Punjab)** (Mughal heritage, Walled City, cultural food streets, museums)
3. **Karachi (Sindh)** (Arabian Sea coast, beaches, maritime history, urban attractions)
4. **Skardu (Gilgit-Baltistan)** (Alpine trekking, cold deserts, glacial lakes, Deosai plains)
5. **Kashmir (Azad Jammu & Kashmir)** (Neelum Valley, high-altitude tarns, pine forests)

All user accounts, multi-destination itineraries, bookings, out-of-pocket expenses, and payment records are permanently stored and queried in Oracle Database.

---

## 2. Technology Stack

| Layer | Component | Description |
|---|---|---|
| **Programming Language** | Python 3.10+ | Clean, procedural, and modular console application |
| **Database Engine** | Oracle Database 26ai | Enterprise relational database (Permanent persistence) |
| **Database Management Tool** | Oracle SQL Developer 26 | SQL script execution, schema compilation & data inspection |
| **Python Database Driver** | `python-oracledb` | Direct Thin Mode connection (no instant client needed) |
| **Initial Datasets** | Microsoft Excel (`.xlsx`) | 17 structured workbooks holding verified tourism data |
| **Excel Ingestion (ETL)** | OpenPyXL / Pandas | Automated one-click ingestion into Oracle tables |
| **Security & Hashing** | Python `hashlib` | Salted SHA-256 password hashing (no plain-text passwords) |
| **Platform** | Windows | Runs via Windows Command Prompt / Terminal or `run.bat` |

---

## 3. Repository Structure

```text
├── 01_Excel_Data/                              # Raw verified datasets (17 Excel workbooks)
│   ├── destinations.xlsx                       # 5 primary destinations
│   ├── destination_guides.xlsx                 # 20 detailed regional travel guides
│   ├── hotels.xlsx                             # 55 verified hotels
│   ├── rooms.xlsx                              # 165 room types & configurations
│   ├── hotel_facilities.xlsx                   # 130 hotel amenities
│   ├── landmarks.xlsx                          # 150 landmarks & tourist attractions
│   ├── trails_trekking.xlsx                    # 70 hiking and alpine trekking routes
│   ├── trail_services.xlsx                     # 80 guide, porter, and permit services
│   ├── activities.xlsx                         # 100 adventure and recreation activities
│   ├── zoos_parks.xlsx                         # 40 wildlife parks and family attractions
│   ├── facility_tickets.xlsx                   # 55 exhibit & attraction entry tickets
│   ├── restaurants.xlsx                        # 100 food street hubs and restaurants
│   ├── food_items.xlsx                         # 111 regional specialty dishes and menus
│   ├── transport_types.xlsx                    # 8 vehicle classes (Jeep, Sedan, Metro, etc.)
│   ├── transport_services.xlsx                 # 45 private rentals and transit services
│   ├── transport_routes.xlsx                   # 25 public transit routes
│   └── public_transport_stops.xlsx             # 110 transit stations and stops
│
├── 02_SQL_Codes/                               # Oracle DDL, DML, and PL/SQL Scripts
│   ├── 01_Create_Tables.sql                    # 28 normalized tables (3NF schema)
│   ├── 02_Add_Primary_Foreign_Keys.sql         # PK and FK relational constraints
│   ├── 03_Add_Constraints.sql                 # CHECK, UNIQUE, and NOT NULL business rules
│   ├── 04_Create_Sequences.sql                 # Oracle sequences for auto-numbering
│   ├── 05_Create_Views.sql                     # Analytical views & reporting queries
│   ├── 06_Create_Procedures.sql                # Stored procedures (trips, bookings, payments)
│   ├── 07_Create_Triggers.sql                  # Audit and automated status triggers
│   ├── 08_Reporting_Queries.sql                # Advanced analytical SQL aggregate queries
│   ├── 09_Useful_Join_Queries.sql              # Multi-table INNER/LEFT join queries
│   ├── 10_Test_Queries.sql                     # Integrity test queries
│   └── 11_Master_Console_Demo.sql              # Master demonstration script for SQL Developer (F5)
│
├── 03_Python_Consol_Based_Application_Codes/   # Python Console Application Source Code
│   ├── main.py                                 # Application entry point & main menu
│   ├── config.py                               # Local Oracle database connection parameters
│   ├── database.py                             # Database connection & query helper functions
│   ├── authentication.py                       # Tourist & Admin authentication with SHA-256
│   ├── destinations.py                         # Destination exploration & side-by-side comparison
│   ├── hotels.py                               # Hotel catalog, filters, and booking
│   ├── landmarks.py                            # Landmarks browser & ticket calculators
│   ├── trails.py                               # Trails, difficulty filters, and guide requirements
│   ├── activities.py                           # Adventure activities & booking
│   ├── zoos_parks.py                           # Zoos, wildlife parks & family cost estimator
│   ├── restaurants.py                          # Restaurants, cuisines & local food menus
│   ├── transportation.py                       # Vehicle rentals & public transit schedules
│   ├── trip_planner.py                         # Multi-destination trip planner & day-by-day scheduler
│   ├── booking.py                              # Centralized booking vouchers & cancellations
│   ├── budget.py                               # Expense tracking, budget vs actual & currency converter
│   ├── checklist.py                            # Travel packing checklist & safety notices
│   ├── admin.py                                # Admin dashboard, user travel audit & live counts
│   ├── data_import.py                          # Automated Excel-to-Oracle ETL importer
│   └── test_system.py                          # Automated test suite
│
├── run.bat                                     # Windows launcher script (one-click run)
└── README.md                                   # Project documentation
```

---

## 4. Database Design & Implementation

The relational schema is designed in **Third Normal Form (3NF)** to eliminate redundancy and maintain referential integrity.

### Schema Summary:
- **Total Tables:** 28 Relational Tables
- **Total Records:** 1,270 verified entries
- **Primary & Foreign Keys:** Full referential integrity defined with `ON DELETE CASCADE` or restricted deletes where appropriate.
- **Constraints:**
  - Rating checks (`RATING BETWEEN 1.0 AND 5.0`)
  - Status domains (`STATUS IN ('ACTIVE', 'INACTIVE')`)
  - Financial checks (`PRICE >= 0`, `BUDGET_PKR > 0`)
  - Pricing models (`Per Person`, `Per Vehicle`, `Per Boat`, `Per Group`, etc.)
- **Stored Procedures:**
  - `SP_CREATE_TRIP`: Creates multi-day journey with auto-generated itinerary structure.
  - `SP_CONFIRM_BOOKING`: Validates availability, calculates pricing, and issues unique voucher numbers (`PV-BKG-XXXXX`).
  - `SP_RECORD_PAYMENT`: Logs transaction and automatically marks booking status as `PAID`.
- **Triggers:**
  - `TRG_UPDATE_BOOKING_ON_PAYMENT`: Updates payment flags in bookings upon receipt entry.
  - `TRG_AUDIT_USER_REGISTRATION`: Logs registration timestamps and security audit entries.
- **Database Views:**
  - `VW_DESTINATION_SUMMARY`: Aggregates total hotels, landmarks, trails, and activities per region.
  - `VW_TRIP_FINANCIAL_OVERVIEW`: Calculates budget variances, confirmed bookings value, and recorded receipts.

---

## 5. Key Application Features

### A. Tourist Module
1. **Secure Registration & Login:** Full validation for username, age, email format, and password confirmation with salted SHA-256 hash encryption.
2. **Destination Exploration:** Comprehensive guides, best visiting seasons, weather advisory, and regional food recommendations.
3. **Multi-Destination Trip Planner:** Plan a single vacation covering multiple destinations (e.g., *Islamabad $\rightarrow$ Skardu $\rightarrow$ Kashmir*) with start/end dates, traveler counts, and planned budgets.
4. **Day-wise Itinerary Scheduler:** Break down daily trips into Morning, Afternoon, Evening, and Night time slots with cost tracking.
5. **Academic Service Bookings:** Reserve hotels, alpine guide services, 4x4 jeeps, and adventure activities with instant voucher generation.
6. **Expense Tracking & Budget Reconciliation:** Log cash/card receipts against planned budgets, compute per-person splits, and view foreign currency conversions (USD, EUR, GBP, SAR, AED).
7. **Travel Packing Checklist:** Region-specific checklist (warm clothing, medical kits, cash warnings for northern areas).

### B. Administrator Module
1. **User Profile & Traveler Audit:** Inspect registered tourists, registration timestamps, and account status.
2. **Complete Chronological Travel History Transcript:** Displays a tourist's entire journey, day-by-day itinerary, booked services, and total financial footprint in one formatted audit transcript.
3. **Analytical Revenue Reports:** Advanced multi-table join and aggregate queries showing gross booking value, settled payments, and destination popularity.
4. **Live Table Inventory:** Real-time SQL record counts across all database tables.
5. **Manage Tourism Records (CRUD):** Administrative ability to add new hotels, attractions, or services directly to Oracle.

---

## 6. Installation & Setup Guide

### Prerequisites
- Windows 10 / 11
- Python 3.10 or newer (ensure Python is checked under **Add to PATH** during installation)
- Oracle Database 26ai (or Oracle XE 21c / 19c)
- Oracle SQL Developer 26

### Step 1: Install Python Dependencies
Open Command Prompt in the project folder and run:
```cmd
pip install oracledb openpyxl pandas
```

### Step 2: Set Up Database Schema in Oracle SQL Developer
1. Open **Oracle SQL Developer** and connect to your database user (e.g., `SYSTEM`).
2. Run the SQL scripts from the `02_SQL_Codes` directory in order:
   - `01_Create_Tables.sql`
   - `02_Add_Primary_Foreign_Keys.sql`
   - `03_Add_Constraints.sql`
   - `04_Create_Sequences.sql`
   - `05_Create_Views.sql`
   - `06_Create_Procedures.sql`
   - `07_Create_Triggers.sql`

*(Alternatively, open `11_Master_Console_Demo.sql` and press **F5** to run the complete automated console demo inside SQL Developer).*

### Step 3: Configure Database Credentials
Open `03_Python_Consol_Based_Application_Codes/config.py` and verify your local database settings:
```python
ORACLE_CONFIG = {
    "user": "SYSTEM",            # Your Oracle database username
    "password": "YOUR_PASSWORD", # Your Oracle database password
    "host": "localhost",
    "port": 1521,
    "service_name": "FREEPDB1"   # Default service name for Oracle 26ai Free
}
```

### Step 4: Import Excel Data into Oracle
Run the automated ETL pipeline to populate the 1,270 records:
```cmd
python 03_Python_Consol_Based_Application_Codes/data_import.py
```

---

## 7. How to Run the Application

### Option 1: Double-Click Batch File (Recommended)
Double-click **`run.bat`** from the project root folder.

### Option 2: Run via Command Prompt
```cmd
cd 03_Python_Consol_Based_Application_Codes
python main.py
```

### Default Credentials:
- **Tourist Account:** Register a new account via Option `[1]`, or sign in with any registered user.
- **Administrator Account:**
  - **Username:** `bilal`
  - **Password:** `ROMAN`

---

## 8. Viva Demonstration Guide

When presenting this project during the lab viva:
1. **Demonstrate Persistence:** Create a new tourist account, plan a multi-city trip, and make a hotel booking. Close the console completely, reopen it, log back in, and show that all data is retrieved live from Oracle Database.
2. **Demonstrate Relational Integrity:** Show how foreign keys prevent orphaned bookings and how the database triggers automatically update booking payment statuses.
3. **Show SQL Developer Integration:** Run `02_SQL_Codes/11_Master_Console_Demo.sql` by pressing **F5** in SQL Developer to demonstrate that the PL/SQL stored procedures and views work natively in Oracle.
4. **Show Admin Oversight:** Sign in as admin (`bilal`), navigate to Option `[5]`, and generate the **Chronological User Travel History Transcript** to showcase complete audit capability.
