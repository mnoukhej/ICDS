# Main_Func.py

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
def Format_Generator(month, year, polio_day, folder_location):
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
        
        
        # Format the decimal places for Current Stock and New Stock columns
        df[('', 'Current Stock')] = df[('', 'Current Stock')].apply(lambda x: f"{float(x):.3f}" if x and str(x).replace('.','',1).isdigit() else x)
        df[('', 'New Stock')] = df[('', 'New Stock')].apply(lambda x: f"{float(x):.3f}" if x and str(x).replace('.','',1).isdigit() else x)
        
        # Add Polio Campaign Day column if polio_day is not None
        if polio_day is not None:
            # Create a list where first element is the date and others are empty
            polio_col = [polio_day] + [''] * (len(food_items)-1)
            df[('', 'Polio Day')] = polio_col
        
        return df





    df_report = generate_day_names(month, year)
    df_stock = generate_stock_sheet()

    # Flatten the MultiIndex columns for easier handling in Excel
    df_report.columns = [' '.join(col).strip() for col in df_report.columns.values]
    df_stock.columns = [' '.join(col).strip() for col in df_stock.columns.values]

    # Generate dynamic filename based on month and year
    month_name = pd.Timestamp(year, month, 1).strftime('%B')
    output_filename = f"{month_name}_{year}_Report_Format.xlsx"
    output_path = os.path.join(folder_location, output_filename)

    # output_path = fr"C:\Users\MUHAMMAD NOUKHEZ\Dropbox\ICDS Report\Report_Format\{output_filename}"
    # output_path = fr"C:\Users\MUHAMMAD NOUKHEZ\Downloads\{output_filename}"


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
def Report_Generator_py(file_path, folder_location):

    # ---------------------------
    # 1️⃣ Validate Input File
    # ---------------------------
    if not os.path.exists(file_path):  
        return (f"Error: The file {file_path} does not exist.")
    # Extract filename from path
    filename = os.path.basename(file_path)

    match = re.search(r"([A-Za-z]+)_(\d{4})", filename) # Use regex to extract month and year

    if match:
        month_name, year = match.groups()
        output_filename = f"{month_name}_{year}_Report.xlsx"
        output_path = os.path.join(folder_location, output_filename)
        
        # output_path = os.path.join(r"C:\Users\MUHAMMAD NOUKHEZ\Downloads", output_filename)
        # print("Generated Output Path:", output_path)
    else:
        print("Error: Could not extract month and year from the filename.")


    month = datetime.strptime(month_name, "%B").month  # Convert month name to number
    year = int(year)  # Ensure year is an integer

    # Generate date range
    date_range = pd.date_range(
        start=f'{year}-{month:02d}-01', 
        end=f'{year}-{month:02d}-{pd.Timestamp(year, month, 1).days_in_month}'
    )


    # === READ SHEETS ===
    icds_sheet = pd.read_excel(file_path, sheet_name='Report Format')
    stock_sheet = pd.read_excel(file_path, sheet_name='Stocks')



    # === CLEAN STOCK SHEET ===

    if 'SL. No' in stock_sheet.columns:     
        stock_sheet = stock_sheet.drop(columns=['SL. No'])  # Drop the 'SL. No' column if it exists
        
    polio_day = int(stock_sheet.loc[0, 'Polio Day']) if 'Polio Day' in stock_sheet.columns else 0

    # Build the nested dictionary with "Current Blance" added
    stock_data = {
        'Food Items': {
            row['Food Items']: {
                'Current Stock': row['Current Stock'],
                'New Stock': row['New Stock'],
                'Date': row['Date'],
            }
            for _, row in stock_sheet.iterrows()
        }
    }


    # === DEFINE RATIO SETTINGS ===
    rice_days = ["Monday", "Wednesday", "Friday"]
    khichdi_days = ["Tuesday", "Thursday", "Saturday", "Sunday"]
    all_days = rice_days + khichdi_days  # Dynamically combines both lists

    # Unified food ratios
    food_ratios = {
        "mothers": {
            "rice": [(rice_days, 0.110), (khichdi_days, 0.075)],
            "daal": [(khichdi_days, 0.030)],
            "oil": [(all_days, 0.002)],
            "salt": [(all_days, 0.002)]
        },
        "children": {
            "rice": [(rice_days, 0.050), (khichdi_days, 0.075)],
            "daal": [(khichdi_days, 0.030)],
            "oil": [(all_days, 0.002)],
            "salt": [(all_days, 0.002)]
        }
    }
    
    
    
    # Ensure 'Date' column is numeric
    icds_sheet['Date'] = pd.to_numeric(icds_sheet['Date'], errors='coerce')

    # Get Daal stock date
    daal_date = stock_data['Food Items']['Daal']['Date']

    # Only check if date is non-zero
    if daal_date != 0:
        match = icds_sheet.loc[icds_sheet['Date'] == daal_date, 'Days']

        if not match.empty:
            day_name = match.values[0]
            if day_name in rice_days:
                stock_data['Food Items']['Daal']['Date'] += 1
        else:
            print(f"⚠ No matching date {daal_date} found in icds_sheet")







    # ======== HELPER FUNCTIONS ========

    def convert_to_int(value):
        if value == "-": return value
        if pd.isna(value): return 0
        try: return int(value)
        except ValueError: return 0

    def convert_to_float(value):
        if value == "-": return value
        if pd.isna(value): return np.nan
        try: return float(value)
        except ValueError: return np.nan

    def replace_multiple_hyphens(value):
        if isinstance(value, str):
            return re.sub(r'-+', '-', value)
        return value


    def calculate_children_MorningSnacks(row):
        if pd.notna(row["total_children"]) and row["Days"] in ["Tuesday", "Thursday", "Saturday"]:
            return round(row["total_children"] * 0.8)  # Apply rounding
        else:
            return "-"
        
        
    # Function to calculate Grand Total with special handling
    def calculate_grand_total(row):
        total_mothers = row["Total Mothers"]
        total_children = row["Total Children"]
        if total_mothers == "-" and total_children == "-": "-"
        if pd.isna(total_mothers) and pd.isna(total_children): return np.nan
        if total_mothers == "-": return total_children
        if total_children == "-": return total_mothers

        return total_mothers + total_children


    def assign_food_days(row, total_column, Days, rice_days, Khichdi_days):
        if row[total_column] == "-": return "-", "-"
        if pd.isna(row[total_column]): return np.nan, np.nan
        if row[Days] in rice_days: return row[total_column], "-"
        elif row[Days] in Khichdi_days: return "-", row[total_column]
        else: return "-", "-"


    def get_ratio_for_day(day, item_ratios):
        for days_list, ratio in item_ratios:
            if day in days_list:
                return ratio
        return None


    def calculate_food_amount(row, total_column, item_ratios):
        if pd.isna(row[total_column]):  
            return np.nan
        if row[total_column] == "-":  
            return "-"
        ratio = get_ratio_for_day(row["Days"], item_ratios)
        return row[total_column] * ratio if ratio is not None else None




    def calculate_total_expenditure(icds_sheet, food_item):
    
        col_mothers = f"{food_item} for Mothers"
        col_children = f"{food_item} for Children"
        total_col = f"Total {food_item} Exp."

        # Check if both required columns exist
        if col_mothers in icds_sheet.columns and col_children in icds_sheet.columns:
            icds_sheet[total_col] = icds_sheet[col_mothers] + icds_sheet[col_children]
        else:
            print(f"Warning: Missing column(s) for '{food_item}': "
                f"{'[Mothers]' if col_mothers not in icds_sheet.columns else ''} "
                f"{'[Children]' if col_children not in icds_sheet.columns else ''}")
            
        return total_col



    def calculate_balance_column(icds_sheet, food_item, stock_data):
    
        total_exp_col = f"Total {food_item} Exp."
        balance_col = f"{food_item} Balance"

        # Fetch stock info
        stock_info = stock_data['Food Items'][food_item]
        initial_balance = stock_info['Current Stock']
        new_stock = stock_info['New Stock']
        reset_date = stock_info['Date']

        balance_list = []
        current_balance = initial_balance

        for _, row in icds_sheet.iterrows():
            total_exp = pd.to_numeric(row.get(total_exp_col, 0), errors='coerce')

            if pd.isna(total_exp):
                balance_list.append("-")
                continue

            if row['Date'] == reset_date:
                current_balance += new_stock

            if current_balance <= 0:
                balance_list.append("-")
            else:
                current_balance -= total_exp
                if current_balance < 0:
                    balance_list.append("-")
                    current_balance = 0
                else:
                    balance_list.append(f"{current_balance:.3f}")  # format as string with 3 decimals


        icds_sheet[balance_col] = balance_list
        return icds_sheet


    def shift_balance_to_next(icds_sheet, item_name, khichdi_days=None):
        """
        Adjusts Total Exp. based on Balance.
        
        - For Daal: if Balance < Total Exp, put Balance in the next Khichdi day row.
        - For Oil, Salt: if Balance < Total Exp, put Balance in the immediate next row.
        """
        balance_col = f"{item_name} Balance"
        exp_col = f"Total {item_name} Exp."

        if balance_col not in icds_sheet.columns or exp_col not in icds_sheet.columns:
            print(f"⚠ Columns missing: Cannot adjust {item_name}")
            return icds_sheet

        balance = pd.to_numeric(icds_sheet[balance_col], errors="coerce")
        exp = pd.to_numeric(icds_sheet[exp_col], errors="coerce")

        for i in range(len(icds_sheet) - 1):
            if pd.notna(balance.iloc[i]) and balance.iloc[i] != 0:
                if pd.notna(exp.iloc[i]) and balance.iloc[i] < exp.iloc[i]:

                    if item_name.lower() == "daal" and khichdi_days is not None:
                        # find the next Khichdi day row
                        next_rows = icds_sheet[(icds_sheet.index > i) & (icds_sheet["Days"].isin(khichdi_days))]
                        if not next_rows.empty:
                            next_idx = next_rows.index[0]
                            icds_sheet.at[next_idx, exp_col] = balance.iloc[i]

                    else:  # Oil or Salt → just next row
                        icds_sheet.at[i+1, exp_col] = balance.iloc[i]

        return icds_sheet
    


    def recalc_all_totals(icds_sheet, total_label="Total"):
        """
        Recalculate 'Total' row for Daal, Oil, and Salt expenditure columns.
        """
        target_columns = ["Total Daal Exp.", "Total Oil Exp.", "Total Salt Exp."]

        # locate the "Total" row
        total_row = icds_sheet[icds_sheet["Days"] == total_label]
        if total_row.empty:
            print(f"⚠ No '{total_label}' row found.")
            return icds_sheet

        total_index = total_row.index[0]

        for col in target_columns:
            if col in icds_sheet.columns:
                # sum excluding the total row itself
                new_total = pd.to_numeric(icds_sheet.loc[icds_sheet.index != total_index, col], errors="coerce").sum()
                icds_sheet.at[total_index, col] = round(new_total, 3)  # keep 3 decimals

        return icds_sheet



    # Regular expression to extract month and year
    match = re.search(r'\\([A-Za-z]+)_(\d{4})_', file_path)

    if match:
        month = match.group(1)  # Extracts the month (e.g., 'January')
        year = match.group(2)   # Extracts the year (e.g., '2024')

        

    # === PREPARE ICDS SHEET ===
    columns_to_convert = [      # Apply the function to relevant columns

        'Pregnant (Mothers)', 
        'Lactating (Mothers)', 
        'Boys (6m - 3y)', 
        'Girls (6m - 3y)', 
        'Boys (3y - 6y)', 
        'Girls (3y - 6y)'
    ]

    for col in columns_to_convert:
        icds_sheet[col] = icds_sheet[col].apply(convert_to_int)
        
        
    icds_sheet["Total Mothers"] = icds_sheet["Pregnant (Mothers)"] + icds_sheet["Lactating (Mothers)"]
    icds_sheet["Total Children"] = (icds_sheet["Boys (6m - 3y)"] + icds_sheet["Girls (6m - 3y)"] + icds_sheet["Boys (3y - 6y)"] + icds_sheet["Girls (3y - 6y)"])




    icds_sheet[["Mothers Rice Day", "Mothers Khichdi Day"]] = icds_sheet.apply(assign_food_days, axis=1, result_type="expand",args=("Total Mothers", "Days", rice_days, khichdi_days))
    icds_sheet[["Children Rice Day", "Children Khichdi Day"]] = icds_sheet.apply(assign_food_days, axis=1, result_type="expand", args=("Total Children", "Days", rice_days, khichdi_days))



    icds_sheet.insert(4, "Total Mothers", icds_sheet.pop("Total Mothers"))
    icds_sheet = icds_sheet.apply(lambda col: col.map(replace_multiple_hyphens))
    icds_sheet.insert(4, "Mothers Rice Day", icds_sheet.pop("Mothers Rice Day"))
    icds_sheet.insert(5, "Mothers Khichdi Day", icds_sheet.pop("Mothers Khichdi Day"))

    icds_sheet["Total Mothers"] = icds_sheet["Total Mothers"].apply(convert_to_float)
    icds_sheet["Total Children"] = icds_sheet["Total Children"].apply(convert_to_float)





    # === APPLY CALCULATIONS FOR BOTH GROUPS ===
    for group in ["mothers", "children"]:
        total_col = f"Total {group.capitalize()}"
        for item, ratios in food_ratios[group].items():
            col_name = f"{item.capitalize()} for {group.capitalize()}"
            icds_sheet[col_name] = icds_sheet.apply(
                calculate_food_amount,
                axis=1,
                args=(total_col, ratios)
            )



    icds_sheet["total_children"] = pd.to_numeric(icds_sheet["Total Children"], errors='coerce')
    icds_sheet["Morning Snacks"] = icds_sheet.apply(calculate_children_MorningSnacks, axis=1)
    icds_sheet = icds_sheet.drop(columns=["total_children"])
    columns = list(icds_sheet.columns)
    columns.insert(columns.index("Days") + 1, columns.pop(columns.index("Morning Snacks")))
    icds_sheet = icds_sheet[columns]
    icds_sheet = icds_sheet.apply(lambda col: col.map(replace_multiple_hyphens))

    


    icds_sheet["Grand Total"] = icds_sheet.apply(calculate_grand_total, axis=1)
    icds_sheet[["Grand Total Rice Day", "Grand Total Khichdi Day"]] = icds_sheet.apply(assign_food_days, axis=1, result_type="expand", args=("Grand Total", "Days", rice_days, khichdi_days))

    icds_sheet["Grand Total Rice Day"] = icds_sheet["Grand Total Rice Day"].apply(convert_to_int)
    icds_sheet["Grand Total Khichdi Day"] = icds_sheet["Grand Total Khichdi Day"].apply(convert_to_int)


    # Original columns list
    columns_order = icds_sheet.columns.tolist()

    # Indices of mothers food columns in the original
    mothers_food_cols = ["Rice for Mothers", "Daal for Mothers", "Oil for Mothers", "Salt for Mothers"]

    # Build new order without duplication
    new_columns_order = (
        columns_order[:7]  # First 7 columns
        + mothers_food_cols
        + [col for col in columns_order[7:] if col not in mothers_food_cols]  # Skip duplicates
    )

    # Reorder DataFrame
    icds_sheet = icds_sheet[new_columns_order]
    icds_sheet = icds_sheet.apply(lambda col: col.map(replace_multiple_hyphens))



    # Loop through each food item from stock_data and calculate total expenditure
    for food_item in stock_data['Food Items']:
        calculate_total_expenditure(icds_sheet, food_item)
        icds_sheet = calculate_balance_column(icds_sheet, food_item, stock_data)


    icds_sheet = icds_sheet.apply(lambda col: col.map(replace_multiple_hyphens))



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
    Oil_data_update = ["Total Oil Exp.", "Oil for Children", "Oil for Mothers"]
    salt_data_update = ["Total Salt Exp.", "Salt for Children", "Salt for Mothers"]


    # Fix dtype before assigning '-'
    for col_group in [daal_data_update, Oil_data_update, salt_data_update]:
        for col in col_group:
            if col in icds_sheet.columns:
                icds_sheet[col] = icds_sheet[col].astype(object)

    icds_sheet.loc[icds_sheet["Daal Balance"] == "-", daal_data_update] = "-"
    icds_sheet.loc[icds_sheet["Oil Balance"] == "-", Oil_data_update] = "-"
    icds_sheet.loc[icds_sheet["Salt Balance"] == "-", salt_data_update] = "-"

    # Format floats without applymap deprecation warning
    icds_sheet = icds_sheet.apply(
        lambda col: col.map(lambda x: f"{x:.3f}" if isinstance(x, float) else x)
    )

    # Drop the specified columns
    columns_to_drop = ["Total Mothers", "Total Children", "Grand Total"]
    icds_sheet = icds_sheet.drop(columns=columns_to_drop, errors='ignore')
    # icds_sheet = icds_sheet.applymap(lambda x: f"{x:.3f}" if isinstance(x, float) else x)

    columns_to_convert = [
        "Lactating (Mothers)", "Mothers Rice Day", "Mothers Khichdi Day",
        "Boys (6m - 3y)", "Girls (6m - 3y)", "Boys (3y - 6y)", "Girls (3y - 6y)",
        "Children Rice Day", "Children Khichdi Day"
    ]
    for col in columns_to_convert:
        icds_sheet[col] = icds_sheet[col].apply(convert_to_int)
        

   # Apply adjustments
    icds_sheet = shift_balance_to_next(icds_sheet, "Daal", khichdi_days)
    icds_sheet = shift_balance_to_next(icds_sheet, "Oil")
    icds_sheet = shift_balance_to_next(icds_sheet, "Salt")    
            
    icds_sheet = recalc_all_totals(icds_sheet)


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
    icds_sheet = icds_sheet.applymap(lambda x: f"{x:.3f}" if isinstance(x, float) else x)


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
        
    # Columns where you want to set width
    columns_to_resize = [18, 24, 25, 27, 29, 31]

    # Apply the same width to each
    for col_num in columns_to_resize:
        ws.column_dimensions[get_column_letter(col_num)].width = 7.5

    # Protect worksheet
    ws.protection.sheet = True
    ws.protection.enable()

    # Save workbook
    wb.save(output_path)
    print("Workbook saved successfully!")
    print(f"Output path: {output_path}")

    return icds_sheet