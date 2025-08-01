import os
import sys
import time
from Main_Func import Report_Generator_py

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_progress(progress):
    """Display a simple progress bar."""
    bar_length = 30
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f"\rProgress: [{bar}] {int(progress * 100)}%")
    sys.stdout.flush()

def generate_report(file_path):
    """Execute report generator with proper error handling and progress tracking."""
    try:
        print(f"=== ICDS Report Generator ===")
        print(f"\nProcessing file: {file_path}")
        print("This may take some time depending on the file size...\n")
        
        start_time = time.time()
        
        # Simulate progress (replace this with actual progress tracking if possible)
        for i in range(1, 11):
            time.sleep(0.2)  # Simulate processing time
            display_progress(i/10)
        
        # Actual report generation
        Report_Generator_py(file_path)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print("\n✅ Report generation completed successfully!")
        print(f"⏱️  Processing time: {processing_time:.2f} seconds")
        return True
    
    except FileNotFoundError:
        print(f"\n❌ Error: The file was not found at: {file_path}")
        print("Please verify the file path and try again.")
    except PermissionError:
        print("\n❌ Error: Permission denied when accessing the file.")
        print("Please check if the file is open in another program or you have proper permissions.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")
    return False

if __name__ == "__main__":
    clear_screen()
    
    # Hardcoded file path
    file_path = r"C:\Users\MUHAMMAD NOUKHEZ\Downloads\July_2025_Report_Format.xlsx"
    
    # Execute with error handling
    success = generate_report(file_path)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)