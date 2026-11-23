"""
Pak Voyage - Destinations Exploration & Comparison Module
Displays destination overviews, travel guides, and side-by-side destination comparisons.
"""

from database import execute_query

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_all_destinations():
    """Retrieves all active destinations from Oracle."""
    sql = "SELECT DESTINATION_ID, DESTINATION_NAME, PROVINCE_REGION, STATUS FROM DESTINATIONS WHERE STATUS = 'ACTIVE' ORDER BY DESTINATION_ID"
    return execute_query(sql)

def get_destination_details(dest_id):
    """Retrieves full information for a single destination."""
    sql = "SELECT * FROM DESTINATIONS WHERE DESTINATION_ID = :id"
    rows = execute_query(sql, {"id": dest_id})
    return rows[0] if rows else None

def get_destination_guides(dest_id):
    """Retrieves detailed topic guides for a destination."""
    sql = "SELECT TOPIC, TITLE, CONTENT FROM DESTINATION_GUIDES WHERE DESTINATION_ID = :id ORDER BY GUIDE_ID"
    return execute_query(sql, {"id": dest_id})

def display_destination_overview(dest):
    """Displays structured, professional destination overview."""
    print("\n" + "=" * 65)
    print(f"      {GREEN}{BOLD}DESTINATION: {dest['destination_name'].upper()} ({dest['province_region']}){RESET}")
    print("=" * 65)
    print(f"\nDescription:\n  {dest['description']}\n")
    print(f"Best Time to Visit:\n  {dest['best_time_to_visit']}\n")
    if dest.get('weather_guidance'):
        print(f"Weather & Seasonal Guidance:\n  {dest['weather_guidance']}\n")
    if dest.get('popular_food'):
        print(f"Signature Regional Food:\n  {dest['popular_food']}\n")
    if dest.get('safety_tips'):
        print(f"Safety & Travel Advisory:\n  {dest['safety_tips']}\n")
    print("-" * 65)

def display_travel_guides(dest_id, dest_name):
    """Displays comprehensive topic guides for a destination."""
    guides = get_destination_guides(dest_id)
    if not guides:
        print(f"\nNo detailed travel guides currently stored for {dest_name}.")
        return

    print("\n" + "=" * 65)
    print(f"      {GREEN}{BOLD}REGIONAL TRAVEL GUIDES - {dest_name.upper()}{RESET}")
    print("=" * 65)
    for idx, g in enumerate(guides, 1):
        print(f"\n[{idx}] {g['title']} ({g['topic']})")
        print("-" * 65)
        print(f"{g['content']}")
    print("\n" + "=" * 65)

def compare_destinations():
    """
    Side-by-side comparison between two destinations based on actual Oracle metrics.
    """
    dests = get_all_destinations()
    if len(dests) < 2:
        print("\nAt least two destinations are required in Oracle to perform a comparison.")
        return

    print("\n" + "=" * 65)
    print("      PAK VOYAGE - DESTINATION COMPARISON ENGINE")
    print("=" * 65)
    for idx, d in enumerate(dests, 1):
        print(f"  {idx}. {d['destination_name']} ({d['province_region']})")

    try:
        c1 = int(input("\nSelect First Destination (number): ").strip())
        c2 = int(input("Select Second Destination (number): ").strip())
        if c1 < 1 or c1 > len(dests) or c2 < 1 or c2 > len(dests) or c1 == c2:
            print("[ERROR]: Invalid selection. Please pick two different numbers.")
            return
    except ValueError:
        print("[ERROR]: Please enter valid numbers.")
        return

    id1 = dests[c1 - 1]["destination_id"]
    id2 = dests[c2 - 1]["destination_id"]

    d1 = get_destination_details(id1)
    d2 = get_destination_details(id2)

    # Gather metrics
    sql_stats = """
        SELECT 
            (SELECT COUNT(*) FROM HOTELS WHERE DESTINATION_ID = :id) AS HOTELS_CNT,
            (SELECT NVL(ROUND(AVG(PRICE_PER_NIGHT_BASE), 0), 0) FROM HOTELS WHERE DESTINATION_ID = :id) AS AVG_HOTEL_PKR,
            (SELECT COUNT(*) FROM LANDMARKS WHERE DESTINATION_ID = :id) AS LANDMARKS_CNT,
            (SELECT COUNT(*) FROM TRAILS WHERE DESTINATION_ID = :id) AS TRAILS_CNT,
            (SELECT COUNT(*) FROM ACTIVITIES WHERE DESTINATION_ID = :id) AS ACTIVITIES_CNT,
            (SELECT COUNT(*) FROM RESTAURANTS WHERE DESTINATION_ID = :id) AS RESTAURANTS_CNT
        FROM DUAL
    """
    s1 = execute_query(sql_stats, {"id": id1})[0]
    s2 = execute_query(sql_stats, {"id": id2})[0]

    rate1 = f"PKR {s1['avg_hotel_pkr']:,}"
    rate2 = f"PKR {s2['avg_hotel_pkr']:,}"

    print("\n" + "=" * 70)
    print(f"{'METRIC / CRITERIA':<30} | {d1['destination_name'][:18]:<18} | {d2['destination_name'][:18]:<18}")
    print("=" * 70)
    print(f"{'Province / Region':<30} | {d1['province_region'][:18]:<18} | {d2['province_region'][:18]:<18}")
    print(f"{'Best Visiting Season':<30} | {d1['best_time_to_visit'][:18]:<18} | {d2['best_time_to_visit'][:18]:<18}")
    print(f"{'Total Verified Hotels':<30} | {s1['hotels_cnt']:<18} | {s2['hotels_cnt']:<18}")
    print(f"{'Avg Hotel Base Rate (PKR)':<30} | {rate1:<18} | {rate2:<18}")
    print(f"{'Verified Cultural Landmarks':<30} | {s1['landmarks_cnt']:<18} | {s2['landmarks_cnt']:<18}")
    print(f"{'Hiking & Trekking Routes':<30} | {s1['trails_cnt']:<18} | {s2['trails_cnt']:<18}")
    print(f"{'Adventure Activities':<30} | {s1['activities_cnt']:<18} | {s2['activities_cnt']:<18}")
    print(f"{'Restaurants & Food Hubs':<30} | {s1['restaurants_cnt']:<18} | {s2['restaurants_cnt']:<18}")
    print("-" * 70)
    print("SUMMARY COMPARISON GUIDANCE:")
    print(f"- {d1['destination_name']}: {d1['description'][:95]}...")
    print(f"- {d2['destination_name']}: {d2['description'][:95]}...")
    print("=" * 70)
