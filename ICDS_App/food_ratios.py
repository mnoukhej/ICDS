# food_ratios.py
# Food allocation ratios and schedule configurations for ICDS Report Generation.
# Edit this file anytime to modify days, ratios, or morning snacks formulas.

import pandas as pd

# ----------------------------------------------------------------------
# 1. Schedule Days Configuration
# ----------------------------------------------------------------------
rice_days = ["Monday", "Wednesday", "Friday"]
khichdi_days = ["Tuesday", "Thursday", "Saturday", "Sunday"]
all_days = rice_days + khichdi_days

# ----------------------------------------------------------------------
# 2. Food Allocation Ratios
# Quantities in kg per beneficiary per meal type
# ----------------------------------------------------------------------
food_ratios = {
    "mothers": {
        "rice": [(rice_days, 0.110), (khichdi_days, 0.075)],
        "daal": [(khichdi_days, 0.030)],
        "oil": [(all_days, 0.002)],
        "salt": [(all_days, 0.002)],
    },
    "children": {
        "rice": [(rice_days, 0.050), (khichdi_days, 0.075)],
        "daal": [(khichdi_days, 0.030)],
        "oil": [(all_days, 0.002)],
        "salt": [(all_days, 0.002)],
    },
}

# ----------------------------------------------------------------------
# 3. Morning Snacks Configuration
# ----------------------------------------------------------------------
morning_snacks_days = ["Tuesday", "Thursday", "Saturday"]
morning_snacks_multiplier = 0.8


def calculate_children_MorningSnacks(row):
    """
    Calculate morning snacks for children on scheduled days.
    """
    if pd.notna(row.get("total_children")) and row.get("Days") in morning_snacks_days:
        return round(row["total_children"] * morning_snacks_multiplier)
    else:
        return "-"
