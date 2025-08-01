import os
import sys
import argparse

# Add the app directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, app_dir)

def run_patient_sync():
    """Run the patient sync script"""
    from messaging.scripts.patient_sync_script import main
    main()

def list_scripts():
    """List available scripts"""
    print("Available scripts:")
    print("  patient-sync    - Emit PATIENT_CREATED events for existing patients")
    print("")
    print("Usage:")
    print("  python run_scripts.py patient-sync --help")
    print("  python run_scripts.py patient-sync --dry-run")
    print("  python run_scripts.py patient-sync --batch-size 50")

def main():
    if len(sys.argv) < 2:
        list_scripts()
        return
    
    script_name = sys.argv[1]
    
    # Remove script name from sys.argv so the individual scripts can parse their args
    sys.argv = [sys.argv[0]] + sys.argv[2:]
    
    if script_name == "patient-sync":
        run_patient_sync()
    elif script_name == "list":
        list_scripts()
    else:
        print(f"Unknown script: {script_name}")
        list_scripts()
        sys.exit(1)

if __name__ == "__main__":
    main()
