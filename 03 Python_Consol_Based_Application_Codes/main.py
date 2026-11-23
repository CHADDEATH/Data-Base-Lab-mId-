"""
Pak Voyage - Pakistan Tourism & Travel Management Agency
Main Console Application Entry Point
"""

import os
import sys

# Enable ANSI colors in Windows terminal
os.system("")

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

from database import test_connection, get_connection
from authentication import (
    register_tourist, authenticate_tourist, 
    authenticate_admin, ensure_initial_admin
)
from destinations import (
    get_all_destinations, get_destination_details, 
    display_destination_overview, display_travel_guides, 
    compare_destinations
)
from hotels import display_hotels_menu
from landmarks import display_landmarks_menu
from trails import display_trails_menu
from activities import display_activities_menu
from zoos_parks import display_zoos_menu
from restaurants import display_restaurants_menu
from transportation import display_transportation_menu
from trip_planner import display_my_trips_menu, manage_trip_destinations
from booking import display_my_bookings
from budget import display_budget_dashboard
from checklist import display_checklist_menu
from admin import display_admin_dashboard

def print_banner():
    """Displays the official Pak Voyage application banner with green project name."""
    print("========================================================================")
    print(f"                         {GREEN}{BOLD}PAK VOYAGE{RESET}")
    print(f"         {GREEN}PAKISTAN TOURISM & TRAVEL MANAGEMENT AGENCY{RESET}")
    print("========================================================================")

def main_menu():
    """Main landing screen of the application."""
    print_banner()

    while True:
        print(f"\n{GREEN}{BOLD}MAIN MENU:{RESET}")
        print("  [1] Sign In / Sign Up as Tourist")
        print("  [2] Sign In as Administrator")
        print("  [3] Check Database Connection & Health")
        print("  [0] Exit Application")
        print("------------------------------------------------------------------------")

        choice = input("Enter choice [0-3]: ").strip()

        if choice == "1":
            tourist_auth_menu()
        elif choice == "2":
            admin_login_flow()
        elif choice == "3":
            ok, msg = test_connection()
            status_text = "ONLINE" if ok else "OFFLINE"
            print(f"\n[Database Check]: {status_text} - {msg}")
            input("\nPress Enter to return to Main Menu...")
        elif choice == "0":
            print("\nThank you for using Pak Voyage. Safe travels across Pakistan!\n")
            sys.exit(0)
        else:
            print("[ERROR]: Invalid selection. Please enter 1, 2, 3, or 0.")

def tourist_auth_menu():
    """Sub-menu for tourist authentication."""
    while True:
        print("\n------------------------------------------------------------------------")
        print(f"{GREEN}{BOLD}TOURIST AUTHENTICATION:{RESET}")
        print("  [1] Sign In")
        print("  [2] Create New Account (Register)")
        print("  [0] Back to Main Menu")
        print("------------------------------------------------------------------------")

        choice = input("Enter choice [0-2]: ").strip()

        if choice == "1":
            user = tourist_login_flow()
            if user:
                tourist_dashboard(user)
                break
        elif choice == "2":
            tourist_registration_flow()
        elif choice == "0":
            break
        else:
            print("[ERROR]: Invalid selection. Please enter 1, 2, or 0.")

def tourist_registration_flow():
    """Collects and validates tourist registration fields."""
    print("\n========================================================================")
    print(f"               {GREEN}{BOLD}TOURIST REGISTRATION - CREATE NEW ACCOUNT{RESET}")
    print("========================================================================")
    fname = input("  Full Name                   : ").strip()
    uname = input("  Username                    : ").strip()
    age   = input("  Age (12-120)                : ").strip()
    country = input("  Country                     : ").strip()
    email = input("  Email Address               : ").strip()
    pwd   = input("  Password (min 6 characters) : ").strip()
    cpwd  = input("  Confirm Password            : ").strip()

    ok, msg, uid = register_tourist(fname, uname, age, country, email, pwd, cpwd)
    if ok:
        print(f"\n[SUCCESS]: {msg}")
    else:
        print(f"\n[REGISTRATION FAILED]: {msg}")
    input("\nPress Enter to continue...")

def tourist_login_flow():
    """Authenticates tourist credentials."""
    print("\n========================================================================")
    print(f"                           {GREEN}{BOLD}TOURIST SIGN IN{RESET}")
    print("========================================================================")
    uname = input("  Username : ").strip()
    pwd   = input("  Password : ").strip()

    ok, msg, user = authenticate_tourist(uname, pwd)
    if ok:
        print(f"\n[SUCCESS]: {msg}")
        return user
    else:
        print(f"\n[LOGIN FAILED]: {msg}")
        input("\nPress Enter to continue...")
        return None

def admin_login_flow():
    """Authenticates administrator credentials."""
    print("\n========================================================================")
    print(f"                        {GREEN}{BOLD}ADMINISTRATOR SIGN IN{RESET}")
    print("========================================================================")
    uname = input("  Admin Username : ").strip()
    pwd   = input("  Admin Password : ").strip()

    ok, msg, admin_user = authenticate_admin(uname, pwd)
    if ok:
        print(f"\n[SUCCESS]: {msg}")
        display_admin_dashboard(admin_user)
    else:
        print(f"\n[ACCESS DENIED]: {msg}")
        input("\nPress Enter to continue...")

def tourist_dashboard(current_user):
    """Main dashboard for signed-in tourists."""
    while True:
        print("\n========================================================================")
        print(f"                          {GREEN}{BOLD}TOURIST DASHBOARD{RESET}")
        print(f"  Welcome, {current_user['full_name']} (@{current_user['username']})")
        print("========================================================================")
        print("  [1] Explore Destinations (Islamabad, Lahore, Karachi, Skardu, Kashmir)")
        print("  [2] Destination Comparison Engine")
        print("  [3] My Trips & Itinerary Planner")
        print("  [4] My Bookings & Reservation Vouchers")
        print("  [5] My Travel Expenses & Budget Calculator")
        print("  [6] Travel Packing Checklist & Mountain Safety")
        print("  [7] My Profile")
        print("  [0] Logout")
        print("------------------------------------------------------------------------")

        choice = input("Enter choice [0-7]: ").strip()

        if choice == "1":
            explore_destinations_flow(current_user)
        elif choice == "2":
            compare_destinations()
            input("\nPress Enter to return to Dashboard...")
        elif choice == "3":
            display_my_trips_menu(current_user)
        elif choice == "4":
            display_my_bookings(current_user)
        elif choice == "5":
            display_budget_dashboard(current_user)
        elif choice == "6":
            display_checklist_menu(current_user)
        elif choice == "7":
            display_user_profile(current_user)
        elif choice == "0":
            print(f"\nLogging out {current_user['full_name']}. Goodbye!")
            break
        else:
            print("[ERROR]: Invalid selection.")

def display_user_profile(user):
    """Displays tourist profile details."""
    print("\n========================================================================")
    print(f"                           {GREEN}{BOLD}TOURIST PROFILE{RESET}")
    print("========================================================================")
    print(f"  Full Name            : {user['full_name']}")
    print(f"  Username             : {user['username']}")
    print(f"  Age                  : {user['age']} Years")
    print(f"  Country of Residence : {user['country']}")
    print(f"  Email Address        : {user['email']}")
    reg_date = str(user.get('created_at') or '').split()[0]
    print(f"  Member Since         : {reg_date}")
    print(f"  Account Status       : {user['status']}")
    print("========================================================================")
    input("\nPress Enter to continue...")

def explore_destinations_flow(current_user):
    """Destination selection and exploration loop."""
    while True:
        dests = get_all_destinations()
        print("\n========================================================================")
        print(f"                   {GREEN}{BOLD}PAK VOYAGE - DESTINATION DIRECTORY{RESET}")
        print("========================================================================")
        for idx, d in enumerate(dests, 1):
            print(f"  [{idx}] {d['destination_name']:<35} ({d['province_region']})")
        print("  [0] Back to Tourist Dashboard")
        print("------------------------------------------------------------------------")

        sel = input("Enter destination choice [0-5]: ").strip()
        if sel == "0":
            break
        try:
            d_idx = int(sel) - 1
            if 0 <= d_idx < len(dests):
                explore_single_destination(dests[d_idx], current_user)
            else:
                print("[ERROR]: Invalid destination number.")
        except ValueError:
            print("[ERROR]: Invalid input.")

def explore_single_destination(dest_summary, current_user):
    """Comprehensive single-destination hub menu."""
    dest_id = dest_summary["destination_id"]
    dest_name = dest_summary["destination_name"]

    dest_full = get_destination_details(dest_id)
    display_destination_overview(dest_full)

    while True:
        print(f"\n{GREEN}{BOLD}EXPLORING: {dest_name.upper()}{RESET}")
        print("------------------------------------------------------------------------")
        print("  [1] Hotels and Accommodation")
        print("  [2] Landmarks and Tourist Attractions")
        print("  [3] Trails, Hiking and Trekking Expeditions")
        print("  [4] Fun and Adventure Activities")
        print("  [5] Zoos, Parks and Family Recreation")
        print("  [6] Restaurants and Local Food")
        print("  [7] Transportation (Private Rentals & Public Transit)")
        print("  [8] Read In-Depth Destination Travel Guides")
        print("  [0] Back to Destinations List")
        print("------------------------------------------------------------------------")

        choice = input("Enter choice [0-8]: ").strip()

        if choice == "1":
            display_hotels_menu(dest_id, dest_name, current_user)
        elif choice == "2":
            display_landmarks_menu(dest_id, dest_name)
        elif choice == "3":
            display_trails_menu(dest_id, dest_name, current_user)
        elif choice == "4":
            display_activities_menu(dest_id, dest_name, current_user)
        elif choice == "5":
            display_zoos_menu(dest_id, dest_name)
        elif choice == "6":
            display_restaurants_menu(dest_id, dest_name)
        elif choice == "7":
            display_transportation_menu(dest_id, dest_name, current_user)
        elif choice == "8":
            display_travel_guides(dest_id, dest_name)
            input("\nPress Enter to continue...")
        elif choice == "0":
            break
        else:
            print("[ERROR]: Invalid selection.")

if __name__ == "__main__":
    main_menu()
