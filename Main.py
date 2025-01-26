import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side
from openpyxl.utils import get_column_letter

def generate_day_names(month, year):
    # Generate all dates in the given month and year
    date_range = pd.date_range(start=f'{year}-{month:02d}-01', end=f'{year}-{month:02d}-{pd.Timestamp(year, month, 1).days_in_month}')
    
    # Create DataFrame with day numbers, day names, and additional columns
    df = pd.DataFrame({
        ('', 'Date'): date_range.day,
        ('', 'Days'): date_range.strftime('%A'),
        ('', 'Pregnant(Mothers)'): '',
        ('', 'Lactating(Mothers)'): '',
        ('', 'Boys(6m - 3y)'): '',
        ('', 'Girls(6m - 3y)'): '',
        ('', 'Boys(3y - 6y)'): '',
        ('', 'Girls(3y - 6y)'): '',
    })
    
    return df

# Generate DataFrame for November 2024
month = 1
year = 2025
df = generate_day_names(month, year)

# Flatten the MultiIndex columns for easier handling in Excel
df.columns = [' '.join(col).strip() for col in df.columns.values]

# Define path to save the output Excel file
output_path = r"C:\Users\MUHAMMAD NOUKHEZ\Downloads\Upload_File.xlsx"

# Initialize a new workbook and add a worksheet
wb = Workbook()
ws = wb.active
ws.title = "Row_sheet"

# Set header row with column names
for row in dataframe_to_rows(df, index=False, header=True):
    ws.append(row)

# Define styles
header_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")  # Light blue header background
header_font = Font(bold=True)  # Bold font for headers
light_red_fill = PatternFill(start_color="FFC0C0", end_color="FFC0C0", fill_type="solid")  # Light red fill for Sundays
center_align = Alignment(horizontal="center", vertical="center")
left_align = Alignment(horizontal="left", vertical="center")
header_rotation = Alignment(horizontal="center", vertical="bottom", textRotation=90)  # Rotate header and bottom align

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
    if day_cell.value == "Sunday":
        # Apply light red fill, center alignment, and border to each cell in the row for Sundays
        for cell in row:
            cell.fill = light_red_fill
            cell.alignment = center_align
            cell.border = thin_border
        # Merge cells from the "Day's" column to the last column in the row, excluding the "Date" column
        start_col = get_column_letter(2)  # Start from "Day's" column
        end_col = get_column_letter(ws.max_column)
        ws.merge_cells(f"{start_col}{day_cell.row}:{end_col}{day_cell.row}")
    else:
        # Apply center alignment and border to all cells except the "Day's" column, which is left-aligned
        for cell in row:
            cell.alignment = center_align
            cell.border = thin_border
        day_cell.alignment = left_align  # Left-align the "Day's" column

# Set specific column widths
ws.column_dimensions[get_column_letter(1)].width = 4.5  # Date column
ws.column_dimensions[get_column_letter(2)].width = 10.5 # Day's column
for col_idx in range(3, ws.max_column + 1):
    ws.column_dimensions[get_column_letter(col_idx)].width = 6.5  # Other columns

# Save the workbook
wb.save(output_path)
