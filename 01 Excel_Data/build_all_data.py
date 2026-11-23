"""
Pak Voyage - Complete Tourism Data Builder
Populates all 17 Excel workbooks with verified Pakistan tourism records.
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def save_workbook(filename, headers, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Data"
    
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    border = Border(
        left=Side(style='thin', color='DDDDDD'),
        right=Side(style='thin', color='DDDDDD'),
        top=Side(style='thin', color='DDDDDD'),
        bottom=Side(style='thin', color='DDDDDD')
    )
    
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border
    
    for row_idx, row in enumerate(rows, 2):
        for col_idx, val in enumerate(row, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.border = border
            if isinstance(val, (int, float)):
                cell.alignment = Alignment(horizontal="right")
            else:
                cell.alignment = Alignment(horizontal="left")
                
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)
        
    filepath = os.path.join(DATA_DIR, filename)
    wb.save(filepath)
    print(f"-> Generated {filename}: {len(rows)} rows.")
    return len(rows)

# =========================================================================
# 1. DESTINATIONS (5 Records)
# =========================================================================
destinations_headers = [
    "DESTINATION_ID", "DESTINATION_NAME", "PROVINCE_REGION", "DESCRIPTION", 
    "BEST_TIME_TO_VISIT", "WEATHER_GUIDANCE", "POPULAR_FOOD", "SAFETY_TIPS", "STATUS"
]

destinations_rows = [
    (1, "Islamabad", "Islamabad Capital Territory", 
     "The modern federal capital of Pakistan, nestled against the scenic Margalla Hills. Renowned for its tree-lined avenues, monumental architecture, world-class museums, clean parks, and panoramic hill trails.",
     "October to April", "Mild winters (4C to 18C); warm summers (24C to 38C) with monsoon rains in July-August.",
     "Monal Barbecue, Savour Foods Pulao, Melody Food Park Chapli Kebab, Afghani Tikka, Street Burgers",
     "Follow marked hiking trail signs on Margalla Hills; carry adequate water; observe traffic lane rules.", "ACTIVE"),
    
    (2, "Lahore", "Punjab",
     "The cultural heart and historical soul of Pakistan. Famed for sublime Mughal monuments, bustling walled-city bazaars, colonial garden estates, vibrant literary festivals, and world-renowned food heritage.",
     "November to March", "Cool pleasant winters (6C to 22C); intense summer heat (30C to 44C) May-June; monsoon in July-August.",
     "Fort Road Nihari, Gawalmandi Hareesa, Butt Karahi, Phiki Jalebi, Waris Nihari, Anarkali Chaat",
     "Stay hydrated during hot periods; prefer authorized tourist guides in the Walled City; respect historical monument rules.", "ACTIVE"),
    
    (3, "Karachi", "Sindh",
     "The economic powerhouse and largest metropolis of Pakistan, located on the Arabian Sea coast. Renowned for dynamic coastal life, colonial stone heritage, maritime history, and late-night culinary culture.",
     "November to February", "Pleasant mild winters (14C to 28C) with cool coastal breezes; warm humid summers (28C to 38C).",
     "Burns Road Food Street Kat-a-Kat, Biryani, Boat Basin Barbecue, Sea View Fish Fry, Rabri, Nihari",
     "Observe swimming advisory flags at open beaches; prefer designated beach huts; avoid swimming during rough monsoon tides.", "ACTIVE"),
    
    (4, "Skardu / Gilgit-Baltistan", "Gilgit-Baltistan",
     "The mountaineering capital of Pakistan and gateway to four of the world's 14 eight-thousanders (including K2 and Broad Peak). Features high-altitude plateaus, turquoise glacial lakes, cold deserts, and ancient Tibetan-influenced forts.",
     "May to October", "Pleasant sunny summer days (15C to 26C) with cool nights (5C to 12C); severe sub-zero winters (-10C to -20C) with heavy snow.",
     "Balti Gyaling (Buckwheat pancakes), Marzan, Balti Mamtu (Steamed dumplings), Yak meat dishes, Fresh Dried Apricots",
     "Acclimatize properly to high altitude; hire experienced 4x4 drivers for Deosai and mountain valleys; register permits at checkpoints.", "ACTIVE"),
    
    (5, "Kashmir / Azad Jammu & Kashmir", "Azad Jammu & Kashmir",
     "A breathtaking expanse of lush alpine valleys, cascading waterfalls, pine-covered mountain ridges, and crystal glacial tarns. Includes Neelum Valley, Jhelum Valley, Rawalakot, and high-altitude alpine meadows.",
     "April to October", "Temperate, refreshing summers (12C to 24C); cold winters (-5C to 8C) with snow blocking higher passes like Ratti Gali from November to May.",
     "Traditional Kashmiri Wazwan, Gushtaba, Rista, Kashmiri Kulcha with Pink Noon Chai, Neelum Trout Fish",
     "Check weather alerts for landsliding along Neelum Valley road; carry original CNIC/Passport for border area security checkpoints.", "ACTIVE")
]

# =========================================================================
# 2. DESTINATION GUIDES (20 Records - 4 per destination)
# =========================================================================
guides_headers = ["GUIDE_ID", "DESTINATION_ID", "TOPIC", "TITLE", "CONTENT"]

guides_rows = [
    # Islamabad
    (1, 1, "Nature & Trekking", "Exploring Margalla Hills National Park", 
     "Margalla Hills National Park encompasses over 12,000 hectares featuring diverse flora, birdlife, and leopards. Trails 1 through 6 offer graded ascents from Marghazar Zoo and F-6 up to Daman-e-Koh and Monal. Start morning hikes before 8 AM during summer. Always carry at least 1.5 liters of drinking water."),
    (2, 1, "Culture & Heritage", "Architectural Landmarks and Lok Virsa", 
     "Islamabad blends brutalist modernism with traditional Islamic forms. The iconic Faisal Mosque (designed by Turkish architect Vedat Dalokay) accommodates 100,000 worshippers. Lok Virsa Museum at Shakarparian preserves authentic ethnographic crafts, textiles, and musical heritage from all provinces."),
    (3, 1, "Food Culture", "Dining from Street MARKAZ to Hilltops", 
     "From the hilltop panoramic terraces of Pir Sohawa to the bustling sector commercial markets (F-6 Super Market, F-7 Jinnah Super, F-10 Markaz), Islamabad offers both authentic local street savories and refined international fare. Saidpur Village features heritage mud-brick artisan dining."),
    (4, 1, "Family & Recreation", "Parks, Aviaries and Lake View Park", 
     "Lake View Park on Rawal Lake features boating, Pakistan's largest walk-in bird aviary, motor racing tracks, and picnic lawns. Shakarparian Gardens provides the Pakistan Monument Museum and commemorative trees planted by visiting world leaders."),
    
    # Lahore
    (5, 2, "Historical Heritage", "Navigating the UNESCO Walled City", 
     "Enter through Delhi Gate to explore the 17th-century Shahi Hammam and the mosaic-tiled Wazir Khan Mosque. Walk through the Royal Trail to the UNESCO-inscribed Lahore Fort and magnificent Badshahi Mosque, which stood as the world's largest mosque for over three centuries."),
    (6, 2, "Gastronomy", "The Legendary Food Streets of Lahore", 
     "Lahore's food culture is historic. Fort Road Food Street provides lit views of the Badshahi Mosque alongside traditional handi and barbecue. Gawalmandi and Anarkali offer morning Halwa Puri, Paya, Nihari, and rich dairy lassi."),
    (7, 2, "Gardens & Parks", "Mughal Gardens and Modern Wildlife Sanctuaries", 
     "Visit Shalimar Gardens with its tripartite terraced water cascades built by Emperor Shah Jahan in 1641. For wildlife and family recreation, Lahore Zoo (founded 1872) and the sprawling Safari Zoo on Raiwind Road provide immense zoological diversity."),
    (8, 2, "Arts & Culture", "Museums, The Mall, and Literary Lahore", 
     "Lahore Museum displays priceless Gandharan Buddhist sculpture (including the Fasting Buddha) and Islamic calligraphy. The Mall road preserves Victorian colonial architecture including the GPO, Aitchison College, and Alhamra Arts Council."),
    
    # Karachi
    (9, 3, "Coastal Recreation", "Beaches, Waterfronts and Arabian Sea Islands", 
     "Clifton Beach and Sea View offer camel rides, dune buggies, and seaside walks. Further west, Sandspit and Hawke's Bay provide tranquil waters and green turtle nesting sanctuaries. Manora Island features a restored colonial lighthouse and modern waterfront park."),
    (10, 3, "Colonial Architecture", "Heritage Walk of Saddar and Civil Lines", 
     "Karachi features yellow Gizri-sandstone colonial architecture. Highlights include Frere Hall (featuring Sadequain's ceiling murals), Empress Market in Saddar, Mohatta Palace Museum in Clifton, and the Karachi Port Trust Head Office."),
    (11, 3, "Food Trail", "Nighttime Street Food Culture", 
     "Karachi sleeps late and eats passionately. Burns Road is Pakistan's oldest street-food haven, famous for Waheed's fry kabab and Delhi rabri. Boat Basin in Clifton buzzes until 4 AM with freshly baked cheese parathas and karahi."),
    (12, 3, "Maritime & Museums", "Naval History and National Archives", 
     "The Pakistan Maritime Museum spans a 28-acre park housing a real Daphne-class submarine (PNS Hangor), naval aircraft, and maritime galleries. The National Museum of Pakistan showcases Indus Valley artifacts from Mohenjo-Daro."),
    
    # Skardu
    (13, 4, "High Altitude Treks", "Expeditions to the Baltoro, Concordia and K2", 
     "Skardu is the springboard for the world's greatest non-polar glacier trek: the Baltoro Glacier to Concordia and K2 Base Camp. Requires licensed mountain guides, experienced high-altitude porters, and multi-day expedition camping gear."),
    (14, 4, "Plateaus & Lakes", "Deosai Plains and Crystal Glacial Tarns", 
     "Deosai National Park is the world's second-highest plateau (average elevation 4,114m), home to the Himalayan Brown Bear and wildflowers in July-August. Sheosar Lake, Upper Kachura Lake, and Satpara Lake offer breathtaking turquoise waters and trout fishing."),
    (15, 4, "Tibetan Heritage", "Ancient Forts and Cold Desert Dunes", 
     "Explore the 8th-century Kharpocho Fort overlooking the Indus River, the 400-year-old Shigar Fort (Aga Khan Historic Cities Programme), and Khaplu Palace. Katpana Cold Desert features wind-swept sand dunes surrounded by snow-capped granite peaks."),
    (16, 4, "Safety & Seasons", "High Altitude Acclimatization and Travel Permits", 
     "Skardu is accessible via the Karakoram Highway / Skardu Road or flights to Skardu Airport. Drink 4 to 5 liters of water daily to prevent AMS (Acute Mountain Sickness). Travel insurance covering emergency helicopter evacuation is recommended for remote treks."),
    
    # Kashmir
    (17, 5, "Alpine Valleys", "Journey Through Neelum Valley", 
     "The Neelum River meanders through dense pine forests and jagged green mountains. Key stops include Dhani Waterfall, Kutton, Keran (overlooking the Line of Control), Sharda (site of ancient Sharda Peeth University), and the high hamlet of Kel."),
    (18, 5, "Alpine Lake Treks", "Trekking to Ratti Gali and Chitta Katha", 
     "Ratti Gali Lake (3,700m) is accessed via a 4x4 jeep track from Dowarian followed by a 2-hour moderate hike. Chitta Katha Lake (3,960m) requires an arduous 8-hour trek from Domel. Both lakes are open strictly from late June to late September."),
    (19, 5, "Meadows & Viewpoints", "Arang Kel and Toli Pir Alpine Ridges", 
     "Arang Kel, known as the Pearl of Neelum, is reached via a chairlift across the Neelum River followed by a steep 45-minute pine trail. In Poonch district, Toli Pir and Banjosa Lake offer rolling grassy hills and cool pine forests ideal for family camping."),
    (20, 5, "Culture & Cuisine", "Kashmiri Hospitality and Artisan Handicrafts", 
     "Azad Kashmir is celebrated for hand-woven Pashmina shawls, walnut woodcarvings, and Kashmiri papier-mache. Savor the multi-course Wazwan feast, Gushtaba, and warm pink tea (Noon Chai) served with freshly baked crispy Kulcha.")
]

print("Defined Destinations & Destination Guides datasets.")
