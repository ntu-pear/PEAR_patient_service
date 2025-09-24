import os
import sys

# Add the correct paths to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(os.path.dirname(script_dir))  # Go up to app/
project_root = os.path.dirname(app_dir)  # Go up to project root

# Add both app and project root to path
sys.path.insert(0, app_dir)
sys.path.insert(0, project_root)

# print(f"Script directory: {script_dir}")
# print(f"App directory: {app_dir}")
# print(f"Project root: {project_root}")
# print(f"Python path: {sys.path[:3]}...")

def test_script_imports():
    """Test that all script components can be imported"""
    try:
        print("Testing script imports...")
        
        # Test base script
        from messaging.scripts.base_script import BaseScript
        print("✅ BaseScript imported successfully")
        
        # Test patient sync script
        from messaging.scripts.patient_sync_script import PatientSyncScript
        print("✅ PatientSyncScript imported successfully")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def test_database_connection():
    """Test database connectivity"""
    try:
        print("\\nTesting database connection...")
        
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine, func
        from database import get_database_url
        from app.models.patient import Patient
        
        engine = create_engine(get_database_url())
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            count = db.query(func.count(Patient.id)).scalar()
            print(f"✅ Database connected! Found {count} patients in database")
            
            # Get a sample patient
            sample = db.query(Patient).first()
            if sample:
                print(f"✅ Sample patient: ID={sample.id}, Name={sample.name}")
            else:
                print("⚠️  No patients found in database")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def test_messaging_setup():
    """Test messaging setup"""
    try:
        print("\\nTesting messaging setup...")
        
        from ..messaging.patient_publisher import get_patient_publisher
        
        publisher = get_patient_publisher(testing=True)
        if publisher:
            print("✅ Patient publisher initialized successfully")
            return True
        else:
            print("❌ Failed to initialize patient publisher")
            return False
            
    except Exception as e:
        print(f"❌ Messaging setup failed: {str(e)}")
        return False

def test_script_initialization():
    """Test script initialization"""
    try:
        print("\\nTesting script initialization...")
        
        from messaging.scripts.patient_sync_script import PatientSyncScript
        
        # Test dry-run mode
        script = PatientSyncScript(dry_run=True, batch_size=10)
        print("✅ Script initialized in dry-run mode")
        
        # Test getting count
        total_count = script.get_total_count()
        print(f"✅ Found {total_count} patients to process")
        
        if total_count > 0:
            # Test fetching a small batch
            batch = script.fetch_batch(0, 2)
            print(f"✅ Fetched sample batch of {len(batch)} patients")
            
            if batch:
                patient = batch[0]
                print(f"✅ Sample patient: ID={patient.id}, Name={patient.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Script initialization failed: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("PATIENT SYNC SCRIPT TEST")
    print("=" * 60)
    
    tests = [
        ("Script Imports", test_script_imports),
        ("Database Connection", test_database_connection),
        ("Messaging Setup", test_messaging_setup),
        ("Script Initialization", test_script_initialization),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\\n🎉 All tests passed! The script is ready to use.")
        print("\\nNext steps:")
        print("1. Run in dry-run mode: python run_scripts.py patient-sync --dry-run")
        print("2. Run for real: python run_scripts.py patient-sync")
    else:
        print("\\n⚠️  Some tests failed. Please fix the issues before running the script.")

if __name__ == "__main__":
    main()
