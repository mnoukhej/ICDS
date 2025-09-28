# ---------------------------
# Generate Format
# ---------------------------

import os
from Main_Func import Format_Generator

def clear_screen():
    """Clear the console screen."""
    os.system('cls')

def get_user_input():
    """Get user input for month, year, and optionally polio day with validation."""
    while True:
        try:
            month = int(input("Enter the month (1-12): "))
            if month < 1 or month > 12:
                print("Please enter a month between 1 and 12.")
                continue
                
            year = int(input("Enter the year (e.g., 2025): "))
            if year < 2000 or year > 2100:  # Basic validation
                print("Please enter a year between 2000 and 2100.")
                continue
                
            include_polio = input("Include Polio campaign? (yes/no): ").strip().lower()
            if include_polio in ('yes', 'y'):
                polio_day = int(input("Enter the day for Polio campaign (1-31): "))
                if polio_day < 1 or polio_day > 31:
                    print("Please enter a day between 1 and 31.")
                    continue
            else:
                polio_day = None
                
            return month, year, polio_day
            
        except ValueError:
            print("Please enter valid numbers.")

if __name__ == "__main__":
    
    clear_screen()  # Clear the screen before starting
    
    print("ICDS Report Format Generator")
    print("----------------------------")
    
    # folder_location = r"C:\Users\MUHAMMAD NOUKHEZ\Dropbox\ICDS Report\Report_Format"
    output_folder_location = fr"C:\Users\MUHAMMAD NOUKHEZ\Downloads"
    month, year, polio_day = get_user_input()
    
    if polio_day is not None:
        print(f"\nGenerating data for {month}/{year} with Polio day on {polio_day}...")
    else:
        print(f"\nGenerating data for {month}/{year} without Polio campaign...")
    
    Format_Generator(month, year, polio_day, output_folder_location)
    print("Data generation complete!")