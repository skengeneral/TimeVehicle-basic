import os
import pandas as pd
from datetime import datetime
from pathlib import Path

def save_to_excel(data_cards, custom_columns=None):
    """
    Accepts the array of processed extraction data cards and structures them 
    into a pristine Excel matrix, mapping the columns dynamically based on GitHub rules.
    """
    if not data_cards:
        return "No Data"

    # 📋 If GitHub provided a live layout list over the air, use it. 
    # Otherwise, fall back to the default fallback settings.
    columns_structure = custom_columns if custom_columns else [
        "Business Name",
        "Google Rating",
        "Complete Address",
        "Operating Hours Matrix",
        "Website Link",
        "Phone Number",
        "Google Plus Code",
        "Facebook Handle",
        "Instagram Handle",
        "LinkedIn Handle",
        "Twitter/X Handle"
    ]

    # Re-map the dictionaries into dynamically structured rows
    rows = []
    for card in data_cards:
        row_data = {col: card.get(col, "Not Provided") for col in columns_structure}
        rows.append(row_data)

    df = pd.DataFrame(rows, columns=columns_structure)

    # 🍏🐧 CROSS-PLATFORM SAVE LOCATION PATH DETECTOR
    # This automatically finds the user's desktop on Windows, Mac, or Linux
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"timevehicle1.0_Export_{timestamp}.xlsx"
    
    desktop_dir = Path.home() / "Desktop"
    
    # Check if the Desktop folder exists, otherwise fallback safely to the User's Home folder
    if desktop_dir.exists():
        output_filepath = desktop_dir / filename
    else:
        output_filepath = Path.home() / filename
    
    try:
        # Save out cleanly using pandas engine using the absolute string path
        df.to_excel(str(output_filepath), index=False)
        return os.path.abspath(str(output_filepath))
    except Exception as e:
        print(f"❌ Excel engine generation error: {str(e)}")
        # Ultimate emergency local folder fallback execution
        try:
            df.to_excel(filename, index=False)
            return os.path.abspath(filename)
        except:
            return "Generation Error"

def save_to_word(data_cards):
    """
    Optional fallback documentation generator. Appends social anchors 
    neatly at the bottom of each structural text section.
    """
    pass