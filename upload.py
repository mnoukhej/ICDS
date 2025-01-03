import numpy as np
import pandas as pd
import re
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

output_path = r"C:\Users\MUHAMMAD NOUKHEZ\Downloads\Output\April_2023_Report.xlsx"
file_path = r"C:\Users\MUHAMMAD NOUKHEZ\Downloads\Input\April_2023_Report_Format.xlsx"

icds_sheet = pd.read_excel(file_path, sheet_name='Row_sheet')

# Define the initial balance and the reset date
initial_rice_balance = 718.800
rice_reset_date = 0 
new_rice_balance = 0
current_rice_balance = initial_rice_balance

# Define the initial balance and the reset date
initial_Daal_balance =132.734 
daal_reset_date = 0
new_Daal_balance = 0
current_Daal_balance = initial_Daal_balance

# Define the initial balance and the reset date
initial_Oil_balance = 14.688
oil_reset_date = 0
new_Oil_balance = 0
current_Oil_balance = initial_Oil_balance

# Define the initial balance and the reset date
initial_Salt_balance = 14.688
salt_reset_date = 0
new_Salt_balance = 0
current_Salt_balance = initial_Salt_balance



# Regular expression to extract month and year
match = re.search(r'\\([A-Za-z]+)_(\d{4})_', file_path)

if match:
    month = match.group(1)  # Extracts the month (e.g., 'January')
    year = match.group(2)   # Extracts the year (e.g., '2024')

holidays = {
    '26 January 2023': 'Republic Day',
    '07 March 2023': 'Doljatra',
    '15 April 2023': 'Bengali New Year’s Day',
    '22 April 2023': 'Id-Ul-Fitre',
    '29 June 2023': 'Id-Ud-Zoha',
    '29 July 2023': 'Muharram',
    '15 August 2023': 'Independence Day',
    '21 October 2023': 'Durga Puja (Saptami)',
    '23 October 2023': 'Durga Puja (Nabami)',
    '24 October 2023': 'Durga Puja (Dashami)',
    '15 November 2023': 'Bhatirdwitiya',
    '25 December 2024': 'Christmas Day'
}

# Define the conversion function
def convert_to_int(value):
    if value == "-":
        return value  # Keep '-' as it is
    if pd.isna(value):
        return 0  # Replace NaN with 0
    try:
        return int(value)  # Convert valid numbers to integers
    except ValueError:
        return 0  # Replace invalid entries with 0

# Apply the function to relevant columns
columns_to_convert = [
    'Pregnant (Mothers)', 
    'Lactating (Mothers)', 
    'Boys (6m - 3y)', 
    'Girls (6m - 3y)', 
    'Boys (3y - 6y)', 
    'Girls (3y - 6y)'
]

for col in columns_to_convert:
    icds_sheet[col] = icds_sheet[col].apply(convert_to_int)
    
    
rice_days = ["Monday", "Wednesday", "Friday"]
Khichdi_days = ["Tuesday", "Thursday", "Saturday"]

rice_ratios_mothers = {"Monday": 0.110, "Wednesday": 0.110, "Friday": 0.110, "Tuesday": 0.075, "Thursday": 0.075, "Saturday": 0.075}
daal_ratios_mothers = {"Tuesday": 0.030, "Thursday": 0.030, "Saturday": 0.030}

# Define food ratios for children
rice_ratios_children = {"Monday": 0.050, "Wednesday": 0.050, "Friday": 0.050, "Tuesday": 0.075, "Thursday": 0.075, "Saturday": 0.075}
daal_ratios_children = {"Tuesday": 0.030, "Thursday": 0.030, "Saturday": 0.030}

# Define default ratio for oil and salt
oil_salt_default_ratio = 0.002


# Function to replace multiple hyphens with a single one
def replace_multiple_hyphens(value):
    if isinstance(value, str):  # Only process string values
        return re.sub(r'-+', '-', value)
    return value  # Return non-string values as they are

# Convert columns to float, while handling '-' and NaN
def convert_to_float(value):
    if value == "-":
        return value  
    if pd.isna(value):
        return np.nan  
    try:
        return float(value)  
    except ValueError:
        return np.nan  

def assign_food_days(row, total_column, Days, rice_days, Khichdi_days):
    if row[total_column] == "-":
        return "-", "-"
    if pd.isna(row[total_column]):
        return np.nan, np.nan
    if row[Days] in rice_days:
        return row[total_column], "-"
    elif row[Days] in Khichdi_days:
        return "-", row[total_column]
    else:
        return "-", "-"


# Define the function for Morning Snacks
def calculate_children_MorningSnacks(row):
    if pd.notna(row["total_children"]) and row["Days"] in ["Tuesday", "Thursday", "Saturday"]:
        return round(row["total_children"] * 0.8)  # Apply rounding
    else:
        return "-"


def calculate_food(row, total_column, day_column, food_ratios, default_ratio=None):
    if pd.isna(row[total_column]):  
        return np.nan
    if row[total_column] == "-":  
        return "-"
    ratio = food_ratios.get(row[day_column], default_ratio)
    return row[total_column] * ratio if ratio is not None else None

icds_sheet["Total Mothers"] = icds_sheet["Pregnant (Mothers)"] + icds_sheet["Lactating (Mothers)"]

icds_sheet.insert(4, "Total Mothers", icds_sheet.pop("Total Mothers"))
icds_sheet = icds_sheet.applymap(replace_multiple_hyphens)

icds_sheet[["Mothers Rice Day", "Mothers Khichdi Day"]] = icds_sheet.apply(assign_food_days, axis=1, result_type="expand",args=("Total Mothers", "Days", rice_days, Khichdi_days))
icds_sheet.insert(4, "Mothers Rice Day", icds_sheet.pop("Mothers Rice Day"))
icds_sheet.insert(5, "Mothers Khichdi Day", icds_sheet.pop("Mothers Khichdi Day"))

icds_sheet["Total Mothers"] = icds_sheet["Total Mothers"].apply(convert_to_float)

# Apply calculations for mothers
icds_sheet["Rice for Mothers"] = icds_sheet.apply(calculate_food, axis=1, args=("Total Mothers", "Days", rice_ratios_mothers))
icds_sheet["Daal for Mothers"] = icds_sheet.apply(calculate_food, axis=1, args=("Total Mothers", "Days", daal_ratios_mothers))
icds_sheet["Oil for Mothers"] = icds_sheet.apply(calculate_food, axis=1, args=("Total Mothers", "Days", {}, oil_salt_default_ratio))
icds_sheet["Salt for Mothers"] = icds_sheet["Oil for Mothers"]  # Same as oil

columns_order = icds_sheet.columns.tolist()
new_columns_order = (columns_order[:7] + ["Rice for Mothers", "Daal for Mothers", "Oil for Mothers", "Salt for Mothers"] + columns_order[7:-4])
icds_sheet = icds_sheet[new_columns_order]
icds_sheet = icds_sheet.applymap(replace_multiple_hyphens)

# Calculate "Total Children" as the sum of the specified columns
icds_sheet["Total Children"] = (icds_sheet["Boys (6m - 3y)"] + icds_sheet["Girls (6m - 3y)"] + icds_sheet["Boys (3y - 6y)"] + icds_sheet["Girls (3y - 6y)"])

icds_sheet["total_children"] = pd.to_numeric(icds_sheet["Total Children"], errors='coerce')
icds_sheet["Morning Snacks"] = icds_sheet.apply(calculate_children_MorningSnacks, axis=1)
icds_sheet = icds_sheet.drop(columns=["total_children"])
columns = list(icds_sheet.columns)
columns.insert(columns.index("Days") + 1, columns.pop(columns.index("Morning Snacks")))
icds_sheet = icds_sheet[columns]
icds_sheet = icds_sheet.applymap(replace_multiple_hyphens)

icds_sheet[["Children Rice Day", "Children Khichdi Day"]] = icds_sheet.apply(assign_food_days, axis=1, result_type="expand", args=("Total Children", "Days", rice_days, Khichdi_days))
icds_sheet["Total Children"] = icds_sheet["Total Children"].apply(convert_to_float)

# Apply calculations for children
icds_sheet["Rice for Children"] = icds_sheet.apply(calculate_food, axis=1, args=("Total Children", "Days", rice_ratios_children))
icds_sheet["Daal for Children"] = icds_sheet.apply(calculate_food, axis=1, args=("Total Children", "Days", daal_ratios_children))
icds_sheet["Oil for Children"] = icds_sheet.apply(calculate_food, axis=1, args=("Total Children", "Days", {}, oil_salt_default_ratio))
icds_sheet["Salt for Children"] = icds_sheet["Oil for Children"]  # Same as oil

# Function to calculate rice balance row by row with reset on the specified reset date
def calculate_rice_balance(row):
    global current_rice_balance
    # Ensure "Total Rice Exp." is a numeric value (or treat NaN correctly)
    total_exp = pd.to_numeric(row["Total Rice Exp."], errors="coerce")
    
    if pd.isna(total_exp):  # Check if "Total Rice Exp." is NaN
        return "-" # Return NaN if the row's "Total Rice Exp." is NaN
    elif row["Date"] == rice_reset_date:
        current_rice_balance = current_rice_balance + new_rice_balance  # Reset the balance on the specified reset date
        current_rice_balance -= total_exp
        return current_rice_balance
    elif current_rice_balance <= 0:
        return "-"  # Display "-" if balance is zero or less than the required expenditure
    else:
        current_rice_balance -= total_exp  # Subtract the expenditure from the balance
        if current_rice_balance < 0:
            return "-"
        else:
            return current_rice_balance   

# Function to calculate Daal balance row by row with reset on the specified reset date
def calculate_Daal_balance(row):
    global current_Daal_balance
    # Ensure "Total Rice Exp." is a numeric value (or treat NaN correctly)
    total_exp = pd.to_numeric(row["Total Daal Exp."], errors="coerce")
    
    if pd.isna(total_exp):  # Check if "Total Rice Exp." is NaN
        return "-"   # Return NaN if the row's "Total Rice Exp." is NaN
    elif row["Date"] == daal_reset_date:
        current_Daal_balance = current_Daal_balance + new_Daal_balance  # Reset the balance on the specified reset date
        current_Daal_balance -= total_exp
        return current_Daal_balance
    elif current_Daal_balance <= 0:
        return "-"  # Display "-" if balance is zero or less than the required expenditure
    else:
        current_Daal_balance -= total_exp  # Subtract the expenditure from the balance
        if current_Daal_balance < 0:
            return "-"
        else:
            return current_Daal_balance
        
# Function to calculate Oil balance row by row with reset on the specified reset date
def calculate_Oil_balance(row):
    global current_Oil_balance
    # Ensure "Total Rice Exp." is a numeric value (or treat NaN correctly)
    total_exp = pd.to_numeric(row["Total Oil Exp."], errors="coerce")
    
    if pd.isna(total_exp):  # Check if "Total Rice Exp." is NaN
        return "-"  # Return NaN if the row's "Total Rice Exp." is NaN
    elif row["Date"] == oil_reset_date:
        current_Oil_balance = current_Oil_balance + new_Oil_balance  # Reset the balance on the specified reset date
        current_Oil_balance -= total_exp
        return current_Oil_balance
    elif current_Oil_balance <= 0:
        return "-"  # Display "-" if balance is zero or less than the required expenditure
    else:
        current_Oil_balance -= total_exp  # Subtract the expenditure from the balance
        if current_Oil_balance < 0:
            return "-"
        else:
            return current_Oil_balance
        
# Function to calculate Salt balance row by row with reset on the specified reset date
def calculate_Salt_balance(row):
    global current_Salt_balance
    # Ensure "Total Rice Exp." is a numeric value (or treat NaN correctly)
    total_exp = pd.to_numeric(row["Total Salt Exp."], errors="coerce")
    
    if pd.isna(total_exp):  # Check if "Total Rice Exp." is NaN
        return "-"  # Return NaN if the row's "Total Rice Exp." is NaN
    elif row["Date"] == salt_reset_date:
        current_Salt_balance = current_Salt_balance + new_Salt_balance  # Reset the balance on the specified reset date
        current_Salt_balance -= total_exp
        return current_Salt_balance
    elif current_Salt_balance <= 0:
        return "-"  # Display "-" if balance is zero or less than the required expenditure
    else:
        current_Salt_balance -= total_exp  # Subtract the expenditure from the balance
        if current_Salt_balance < 0:
            return "-"
        else:
            return current_Salt_balance

# Function to calculate Grand Total with special handling
def calculate_grand_total(row):
    total_mothers = row["Total Mothers"]
    total_children = row["Total Children"]
    if total_mothers == "-" and total_children == "-":
        return "-"
    # Handle case where both are NaN
    if pd.isna(total_mothers) and pd.isna(total_children):
        return np.nan
    # Handle case where one of them is "-" and the other is numeric
    if total_mothers == "-":
        return total_children
    if total_children == "-":
        return total_mothers

    return total_mothers + total_children

icds_sheet["Grand Total"] = icds_sheet.apply(calculate_grand_total, axis=1)
icds_sheet[["Grand Total Rice Day", "Grand Total Khichdi Day"]] = icds_sheet.apply(assign_food_days, axis=1, result_type="expand", args=("Grand Total", "Days", rice_days, Khichdi_days))

icds_sheet["Grand Total Rice Day"] = icds_sheet["Grand Total Rice Day"].apply(convert_to_int)
icds_sheet["Grand Total Khichdi Day"] = icds_sheet["Grand Total Khichdi Day"].apply(convert_to_int)

icds_sheet["Total Rice Exp."] = icds_sheet["Rice for Mothers"] + icds_sheet["Rice for Children"]
icds_sheet["Rice Balance"] = icds_sheet.apply(calculate_rice_balance, axis=1)
icds_sheet["Total Daal Exp."] = icds_sheet["Daal for Mothers"] + icds_sheet["Daal for Children"]
icds_sheet["Daal Balance"] = icds_sheet.apply(calculate_Daal_balance, axis=1)
icds_sheet["Total Oil Exp."] = icds_sheet["Oil for Mothers"] + icds_sheet["Oil for Children"]
icds_sheet["Oil Balance"] = icds_sheet.apply(calculate_Oil_balance, axis=1)
icds_sheet["Total Salt Exp."] = icds_sheet["Salt for Mothers"] + icds_sheet["Salt for Children"]
icds_sheet["Salt Balance"] = icds_sheet.apply(calculate_Salt_balance, axis=1)
icds_sheet = icds_sheet.applymap(replace_multiple_hyphens)


temp_sheet = icds_sheet.copy()
for col in temp_sheet.columns.difference(["Date", "Days"]):
    temp_sheet[col] = pd.to_numeric(temp_sheet[col], errors='coerce').fillna(0)

columns_to_sum = temp_sheet.columns.difference(["Date", "Days"])  # Exclude 'Date' and 'Days'
totals = temp_sheet[columns_to_sum].sum()  # Sum numerical columns

columns_with_last_value = ["Rice Balance", "Daal Balance", "Oil Balance", "Salt Balance"]

for col in columns_with_last_value:
    if col in temp_sheet.columns:
        # Get the last non-zero value in the column
        last_value = temp_sheet[col][temp_sheet[col] != 0].iloc[-1]
        totals[col] = last_value

# Create the "Total" row
totals_row = pd.DataFrame([totals], columns=columns_to_sum)
totals_row.insert(0, "Days", "Total")  # Add "Total" in the 'Days' column
totals_row.insert(1, "Date", "")  # Leave 'Date' blank

# Convert specified columns in the "Total" row to integer
columns_to_convert = [
    "Pregnant (Mothers)", "Lactating (Mothers)", "Total Mothers",
    "Boys (6m - 3y)", "Girls (6m - 3y)", "Boys (3y - 6y)",
    "Girls (3y - 6y)", "Total Children", "Grand Total", "Morning Snacks", 
    "Grand Total Rice Day", "Grand Total Khichdi Day", "Children Rice Day",
    "Children Khichdi Day", "Mothers Rice Day", "Mothers Khichdi Day"
]

for col in columns_to_convert:
    if col in totals_row.columns:
        totals_row[col] = totals_row[col].astype(int)

icds_sheet = pd.concat([icds_sheet, totals_row], ignore_index=True)

daal_data_update = ["Total Daal Exp.", "Daal for Children", "Daal for Mothers"]
icds_sheet.loc[icds_sheet["Daal Balance"] == "-", daal_data_update] = "-"
Oil_data_update = ["Total Oil Exp.", "Oil for Children", "Oil for Mothers"]
icds_sheet.loc[icds_sheet["Oil Balance"] == "-", Oil_data_update] = "-"
salt_data_update = ["Total Salt Exp.", "Salt for Children", "Salt for Mothers"]
icds_sheet.loc[icds_sheet["Salt Balance"] == "-", salt_data_update] = "-"

# Drop the specified columns
columns_to_drop = ["Total Mothers", "Total Children", "Grand Total"]
icds_sheet = icds_sheet.drop(columns=columns_to_drop, errors='ignore')
icds_sheet = icds_sheet.applymap(lambda x: f"{x:.3f}" if isinstance(x, float) else x)

columns_to_convert = [
    "Lactating (Mothers)", "Mothers Rice Day", "Mothers Khichdi Day",
    "Boys (6m - 3y)", "Girls (6m - 3y)", "Boys (3y - 6y)", "Girls (3y - 6y)",
    "Children Rice Day", "Children Khichdi Day"
]
for col in columns_to_convert:
    icds_sheet[col] = icds_sheet[col].apply(convert_to_int)
    
    

rename_mapping = {
    "Mothers Rice Day": "Rice Day (Mothers)",
    "Mothers Khichdi Day": "Khichdi Day (Mothers)",
    "Rice for Mothers": "Rice (Mothers)",
    "Daal for Mothers": "Daal (Mothers)",
    "Oil for Mothers": "Oil (Mothers)",
    "Salt for Mothers": "Salt (Mothers)",
    "Boys (6m - 3y)": "Boys (6m - 3y)",
    "Girls (6m - 3y)": "Girls (6m - 3y)",
    "Boys (3y - 6y)": "Boys (3y - 6y)",
    "Girls (3y - 6y)": "Girls (3y - 6y)",
    "Children Rice Day": "Rice Day (Children)",
    "Children Khichdi Day": "Khichdi Day (Children)",
    "Rice for Children": "Rice (Children)",
    "Daal for Children": "Daal (Children)",
    "Oil for Children": "Oil (Children)",
    "Salt for Children": "Salt (Children)",
    "Grand Total Rice Day": "Rice Day (Grand Total)",
    "Grand Total Khichdi Day": "Khichdi Day (Grand Total)"
}

# Rename columns
icds_sheet.rename(columns=rename_mapping, inplace=True)


# Initialize a new workbook and add a worksheet
wb = Workbook()
ws = wb.active
ws.title = "Row_sheet"

# Set header row with column names
for row in dataframe_to_rows(icds_sheet, index=False, header=True):
    ws.append(row)

# Define styles
header_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")  # Light blue header background
header_font = Font(bold=True)  # Bold font for headers
light_red_fill = PatternFill(start_color="FFC0C0", end_color="FFC0C0", fill_type="solid")  # Light red fill for Sundays
holiday_fill = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")  # Yellow fill for holidays
center_align = Alignment(horizontal="center", vertical="center")
left_align = Alignment(horizontal="left", vertical="center")
header_rotation = Alignment(horizontal="center", vertical="bottom", textRotation=90)  # Rotate header and bottom align
total_row_fill = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")  # Green fill for "Total" row

# Define border style
thin_border = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin")
)

# Apply header styles with rotation, bottom alignment, and borders
for cell in ws[1]:
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = header_rotation
    cell.border = thin_border

# Apply styles and borders for each row
for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
    day_cell = row[1]  # Day's column (second column in each row)
    date_cell = row[0]
    snacks_cell = row[2]  # Third column assumed to be "Morning Snacks"


    if day_cell.value == "Sunday":
        for cell in row:
            cell.fill = light_red_fill
            cell.alignment = center_align
            cell.border = thin_border
        ws.merge_cells(f"B{day_cell.row}:{get_column_letter(ws.max_column)}{day_cell.row}")
    else:
        for cell in row:
            cell.alignment = center_align
            cell.border = thin_border
        day_cell.alignment = left_align
        
        
    # Check for "Total" row and apply green fill
    row_text = [cell.value for cell in row if cell.value]  # Get non-empty values in the row
    if "Total" in row_text:
        for cell in row:
            cell.fill = total_row_fill
            cell.alignment = center_align
            cell.border = thin_border
    

# Set specific column widths
ws.column_dimensions[get_column_letter(1)].width = 4.5  # Date column
ws.column_dimensions[get_column_letter(2)].width = 10.5 # Day's column
for col_idx in range(3, ws.max_column + 1):
    ws.column_dimensions[get_column_letter(col_idx)].width = 6.5  # Other columns
    
    
# Save the workbook
wb.save(output_path)

