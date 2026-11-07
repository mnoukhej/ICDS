# food_ratios.py
# Food allocation ratios and schedule configurations for ICDS Report Generation.
# Edit this file anytime to modify days or ratios.

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
# 3. Morning Snacks Configuration Parameters
# ----------------------------------------------------------------------
morning_snacks_days = ["Tuesday", "Thursday", "Saturday"]
morning_snacks_multiplier = 0.8
