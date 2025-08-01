import numpy as np
import pandas as pd
import os
import re
from datetime import datetime
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side

from holiday_list import holidays


# Format_Generator function to create the report format
def Format_Generator(month, year, polio_day):
    def generate_day_names(month, year):
        # Generate all dates in the given month and year
        date_range = pd.date_range(start=f'{year}-{month:02d}-01', end=f'{year}-{month:02d}-{pd.Timestamp(year, month, 1).days_in_month}')
        
        # Create DataFrame with day numbers, day names, and additional columns
        df = pd.DataFrame({
            ('', 'Date'): date_range.day,
            ('', 'Days'): date_range.strftime('%A'),
            ('', 'Pregnant (Mothers)'): '',
            ('', 'Lactating (Mothers)'): '',
            ('', 'Boys (6m - 3y)'): '',
            ('', 'Girls (6m - 3y)'): '',
            ('', 'Boys (3y - 6y)'): '',
            ('', 'Girls (3y - 6y)'): '',
        })
        
        return df


    def generate_stock_sheet():
        # Food items data
        food_items = ['Rice', 'Daal', 'Oil', 'Salt']
        
        # Create base dictionary for DataFrame
        data = {
            ('', 'SL. No'): range(1, len(food_items)+1),
            ('', 'Food Items'): food_items,
            ('', 'Current Stock'): '',
            ('', 'New Stock'): '',
            ('', 'Date'): ''
        }
        
        # Create DataFrame first
        df = pd.DataFrame(data)
        
        # Add Polio Campaign Day column if polio_day is not None
        if polio_day is not None:
            # Create a list where first element is the date and others are empty
            polio_col = [polio_day] + [''] * (len(food_items)-1)
            df[('', 'Polio Campaign Day')] = polio_col
        
        return df





    df_report = generate_day_names(month, year)
    df_stock = generate_stock_sheet()

    # Flatten the MultiIndex columns for easier handling in Excel
    df_report.columns = [' '.join(col).strip() for col in df_report.columns.values]
    df_stock.columns = [' '.join(col).strip() for col in df_stock.columns.values]

    # Generate dynamic filename based on month and year
    month_name = pd.Timestamp(year, month, 1).strftime('%B')
    output_filename = f"{month_name}_{year}_Report_Format.xlsx"
    # output_path = fr"C:\Users\MUHAMMAD NOUKHEZ\Dropbox\ICDS Report\Report_Format\{output_filename}"
    output_path = fr"C:\Users\MUHAMMAD NOUKHEZ\Downloads\{output_filename}"


    # Initialize a new workbook
    wb = Workbook()

    # Create Report Format sheet
    ws_report = wb.active
    ws_report.title = "Report Format"

    # Set header row with column names for Report Format
    for row in dataframe_to_rows(df_report, index=False, header=True):
        ws_report.append(row)

    # Create Stocks sheet
    ws_stock = wb.create_sheet(title="Stocks")

    # Set header row with column names for Stocks
    for row in dataframe_to_rows(df_stock, index=False, header=True):
        ws_stock.append(row)

    # Define styles
    header_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
    header_font = Font(bold=True)
    light_red_fill = PatternFill(start_color="FFC0C0", end_color="FFC0C0", fill_type="solid")
    holiday_fill = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")
    header_rotation = Alignment(horizontal="center", vertical="bottom", textRotation=90)
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    # Define column colors for Stocks sheet
    column_colors = {
        1: "E6E6FA",  # Lavender for SL.No
        2: "E0FFFF",  # Light Cyan for Food Items
        3: "F0FFF0",  # Honeydew for Current Stock
        4: "FFF0F5",  # Lavender Blush for New Stock
        5: "F5F5DC"   # Beige for Date
    }

    # Apply styles to Report Format sheet
    for cell in ws_report[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_rotation
        cell.border = thin_border

    for row in ws_report.iter_rows(min_row=2, max_row=ws_report.max_row, min_col=1, max_col=ws_report.max_column):
        date_cell = row[0]
        day_cell = row[1]
        full_date = f"{date_cell.value:02d} {month_name} {year}"
        
        if full_date in holidays:
            holiday_name = holidays[full_date]
            for cell in row:
                cell.fill = holiday_fill
                cell.alignment = center_align
                cell.border = thin_border
            
            start_col = get_column_letter(3)
            end_col = get_column_letter(ws_report.max_column)
            ws_report.merge_cells(f"{start_col}{date_cell.row}:{end_col}{date_cell.row}")
            ws_report[f"{start_col}{date_cell.row}"].value = holiday_name
            ws_report[f"{start_col}{date_cell.row}"].alignment = center_align
            ws_report[f"{start_col}{date_cell.row}"].font = Font(bold=True)

        elif day_cell.value == "Sunday" and date_cell.value != polio_day:
            for cell in row:
                cell.fill = light_red_fill
                cell.alignment = center_align
                cell.border = thin_border
            ws_report.merge_cells(f"B{day_cell.row}:{get_column_letter(ws_report.max_column)}{day_cell.row}")
        
        else:
            if date_cell.value == polio_day:
                for cell in row:
                    cell.fill = light_red_fill
            for cell in row:
                cell.alignment = center_align
                cell.border = thin_border
            day_cell.alignment = left_align

    # Set column widths for Report Format
    ws_report.column_dimensions[get_column_letter(1)].width = 4.5
    ws_report.column_dimensions[get_column_letter(2)].width = 10.5
    for col_idx in range(3, ws_report.max_column + 1):
        ws_report.column_dimensions[get_column_letter(col_idx)].width = 6.5

    # Apply styles to Stocks sheet
    for cell in ws_stock[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_rotation
        cell.border = thin_border

    # Apply different colors to each column in Stocks sheet
    for col_idx in range(1, ws_stock.max_column + 1):
        color = column_colors.get(col_idx, "FFFFFF")  # Default to white if column not in dictionary
        column_fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
        
        for row in ws_stock.iter_rows(min_row=2, max_row=ws_stock.max_row, min_col=col_idx, max_col=col_idx):
            for cell in row:
                cell.fill = column_fill
                cell.alignment = center_align
                cell.border = thin_border

    # Set column widths for Stocks sheet
    ws_stock.column_dimensions[get_column_letter(1)].width = 4.5  # SL.No
    ws_stock.column_dimensions[get_column_letter(2)].width = 6.5  # Food Items
    ws_stock.column_dimensions[get_column_letter(3)].width = 6.5  # Current Stock
    ws_stock.column_dimensions[get_column_letter(4)].width = 6.5  # New Stock
    ws_stock.column_dimensions[get_column_letter(5)].width = 6.5  # New Stock Date

    # Save the workbook
    wb.save(output_path)

    print(f"File saved as: {output_path}")
    
    return output_path



# Report_Generator_py function to generate the report based on the format
def Report_Generator_py(file_path):
    # Initialize global balance variables
    global current_rice_balance, current_Daal_balance, current_Oil_balance, current_Salt_balance

    # Check if the file exists
    if not os.path.exists(file_path):  
        return (f"Error: The file {file_path} does not exist.")
    # Extract filename from path
    filename = os.path.basename(file_path)

    # Use regex to extract month and year
    match = re.search(r"([A-Za-z]+)_(\d{4})", filename)
    if match:
        month_name, year = match.groups()
        output_filename = f"{month_name}_{year}_Report.xlsx"
        # output_path = os.path.join(r"C:\Users\MUHAMMAD NOUKHEZ\Dropbox\ICDS Report\Report", output_filename)
        output_path = os.path.join(r"C:\Users\MUHAMMAD NOUKHEZ\Downloads", output_filename)
        # print("Generated Output Path:", output_path)
    # else:
    #     print("Error: Could not extract month and year from the filename.")

    # Convert month name to number
    month = datetime.strptime(month_name, "%B").month  # "March" -> 3
    year = int(year)  # Ensure year is an integer


    # Generate date range
    date_range = pd.date_range(
        start=f'{year}-{month:02d}-01', 
        end=f'{year}-{month:02d}-{pd.Timestamp(year, month, 1).days_in_month}'
    )

    icds_sheet = pd.read_excel(file_path, sheet_name='Report Format')
    stock_sheet = pd.read_excel(file_path, sheet_name='Stocks')

    if 'Polio Campaign Day' in stock_sheet.columns:
        polio_day = int(stock_sheet.loc[0, 'Polio Campaign Day'])
    else:
        polio_day = 0
        
    # Define the initial Rice balance and the reset date
    initial_rice_balance = stock_sheet.loc[0, 'Current Stock']  # 803.790
    rice_reset_date = int(stock_sheet.loc[0, 'Date'])               # 0
    new_rice_balance = stock_sheet.loc[0, 'New Stock']         # 0
    current_rice_balance = initial_rice_balance 

    # Define the initial Daal balance and the reset date
    initial_Daal_balance = stock_sheet.loc[1, 'Current Stock']  # 73.500
    daal_reset_date = int(stock_sheet.loc[1, 'Date'])               # 0
    new_Daal_balance = stock_sheet.loc[1, 'New Stock']          # 0
    current_Daal_balance = initial_Daal_balance

    # Define the initial Oil balance and the reset date
    initial_Oil_balance = stock_sheet.loc[2, 'Current Stock']  # 3.672
    oil_reset_date = int(stock_sheet.loc[2, 'Date'])              # 0
    new_Oil_balance = stock_sheet.loc[2, 'New Stock']          # 0
    current_Oil_balance = initial_Oil_balance

    # Define the initial Salt balance and the reset date
    initial_Salt_balance = stock_sheet.loc[3, 'Current Stock']  # 3.672
    salt_reset_date = int(stock_sheet.loc[3, 'Date'])            # 0
    new_Salt_balance = stock_sheet.loc[3, 'New Stock']          # 0
    current_Salt_balance = initial_Salt_balance

    # Regular expression to extract month and year
    match = re.search(r'\\([A-Za-z]+)_(\d{4})_', file_path)

    if match:
        month = match.group(1)  # Extracts the month (e.g., 'January')
        year = match.group(2)   # Extracts the year (e.g., '2024')

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
    Khichdi_days = ["Tuesday", "Thursday", "Saturday","Sunday"]

    rice_ratios_mothers = {"Monday": 0.110, "Wednesday": 0.110, "Friday": 0.110, "Tuesday": 0.075, "Thursday": 0.075, "Saturday": 0.075, "Sunday": 0.075}
    daal_ratios_mothers = {"Tuesday": 0.030, "Thursday": 0.030, "Saturday": 0.030, "Sunday": 0.030}

    # Define food ratios for children
    rice_ratios_children = {"Monday": 0.050, "Wednesday": 0.050, "Friday": 0.050, "Tuesday": 0.075, "Thursday": 0.075, "Saturday": 0.075, "Sunday": 0.075}
    daal_ratios_children = {"Tuesday": 0.030, "Thursday": 0.030, "Saturday": 0.030, "Sunday": 0.030}

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
            current_rice_balance = new_rice_balance  # Reset the balance on the specified reset date
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
            current_Daal_balance = new_Daal_balance  # Reset the balance on the specified reset date
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
            current_Oil_balance = new_Oil_balance  # Reset the balance on the specified reset date
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
            current_Salt_balance = new_Salt_balance  # Reset the balance on the specified reset date
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

    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.utils.dataframe import dataframe_to_rows

    # Initialize a new workbook and add a worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "ICDS Report"

    # Set header row with column names
    for row in dataframe_to_rows(icds_sheet, index=False, header=True):
        ws.append(row)

    balance_columns = ["Rice Balance", "Daal Balance", "Oil Balance", "Salt Balance"]

    # Define styles
    header_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")  # Light blue
    header_font = Font(bold=True)
    light_red_fill = PatternFill(start_color="FFC0C0", end_color="FFC0C0", fill_type="solid")  # Light red for Sundays
    holiday_fill = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")  # Light yellow for holidays
    total_balance_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")  # Yellow for balance cols
    total_row_fill = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")  # Green for Total row

    center_align = Alignment(horizontal="center", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")
    header_rotation = Alignment(horizontal="center", vertical="bottom", textRotation=90)

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    # Apply header styles (and highlight balance columns in yellow)
    for idx, cell in enumerate(ws[1], start=1):
        if cell.value in balance_columns:
            cell.fill = total_balance_fill  # Yellow fill for balance column headers
        else:
            cell.fill = header_fill         # Default header fill

        cell.font = header_font
        cell.alignment = header_rotation
        cell.border = thin_border

    # Get column indices for balance columns
    balance_col_indices = [
        idx + 1 for idx, cell in enumerate(ws[1]) if cell.value in balance_columns
    ]

    # Apply styles and logic to each row
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
        date_cell = row[0]  # Date column
        day_cell = row[1]  # Day column

        # Format date (assumes numeric day in column and provided `month_name`, `year`)
        if date_cell.value and str(date_cell.value).isdigit():
            full_date = f"{int(date_cell.value):02d} {month_name} {year}"
        else:
            full_date = "Invalid Date"

        # Check if it's a holiday
        if full_date in holidays:
            holiday_name = holidays[full_date]
            for cell in row:
                cell.fill = holiday_fill
                cell.alignment = center_align
                cell.border = thin_border
            # Merge and insert holiday name
            start_col = get_column_letter(3)
            end_col = get_column_letter(ws.max_column)
            ws.merge_cells(f"{start_col}{date_cell.row}:{end_col}{date_cell.row}")
            ws[f"{start_col}{date_cell.row}"].value = holiday_name
            ws[f"{start_col}{date_cell.row}"].alignment = center_align
            ws[f"{start_col}{date_cell.row}"].font = Font(bold=True)

        elif day_cell.value == "Sunday" and date_cell.value != polio_day:
            for cell in row:
                cell.fill = light_red_fill
                cell.alignment = center_align
                cell.border = thin_border
            ws.merge_cells(f"B{day_cell.row}:{get_column_letter(ws.max_column)}{day_cell.row}")

        else:
            if date_cell.value == polio_day:
                for cell in row:
                    cell.fill = light_red_fill

            for cell in row:
                cell.alignment = center_align
                cell.border = thin_border
            day_cell.alignment = left_align

        
        # Apply green fill for Total row
        row_text = [cell.value for cell in row if cell.value]
        if "Total" in row_text:
            for cell in row:
                cell.fill = total_row_fill
                cell.alignment = center_align
                cell.border = thin_border
                
        # Apply yellow fill to balance columns
        for col_idx in balance_col_indices:
            row[col_idx - 1].fill = total_balance_fill

    # Set column widths
    ws.column_dimensions[get_column_letter(1)].width = 4.5
    ws.column_dimensions[get_column_letter(2)].width = 10.5
    for col_idx in range(3, ws.max_column + 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 6.5

    # Protect worksheet
    ws.protection.sheet = True
    ws.protection.enable()

    # Save workbook
    wb.save(output_path)
    # print("Workbook saved successfully!")
    # print(f"Output path: {output_path}")
    
    
    # os.system('cls' if os.name == 'nt' else 'clear')
    
    # return output_path  # Return the output path for further use if needed





