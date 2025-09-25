import sys
import os
import argparse
from typing import List, Optional, Dict, Any

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from .base_script import BaseScript

class PatientSyncScript(BaseScript):
    """
    Script to emit PATIENT_CREATED events for existing patients in the database
    """
    
    def __init__(self, dry_run: bool = False, batch_size: int = 100, 
                 check_target: bool = False, target_service_url: Optional[str] = None):
        super().__init__(dry_run, batch_size)
        self.check_target = check_target
        self.target_service_url = target_service_url
        
        # Initialize database and messaging
        self._init_dependencies()
    
    def _init_dependencies(self):
        """Initialize database and messaging dependencies"""
        try:
            # Setup proper Python paths
            script_dir = os.path.dirname(os.path.abspath(__file__))
            current = script_dir
            project_root = None
            
            # Find project root (directory containing 'app')
            for _ in range(5):
                if 'app' in os.listdir(current) and os.path.isdir(os.path.join(current, 'app')):
                    project_root = current
                    break
                parent = os.path.dirname(current)
                if parent == current:
                    break
                current = parent
            
            if not project_root:
                raise RuntimeError("Could not find project root directory containing 'app'")
            
            app_dir = os.path.join(project_root, 'app')
            
            # Add to Python path
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            if app_dir not in sys.path:
                sys.path.insert(0, app_dir)
            
            self.logger.info(f"Project root: {project_root}")
            self.logger.info(f"App directory: {app_dir}")
            
            # Import database dependencies
            from sqlalchemy.orm import sessionmaker
            from sqlalchemy import create_engine, func
            from database import get_database_url
            from app.models.patient_model import Patient
            
            # Import messaging dependencies  
            from messaging.patient_publisher import get_patient_publisher
            
            # Set up database
            engine = create_engine(get_database_url())
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            self.Patient = Patient
            self.func = func
            
            # Set up messaging
            self.publisher = get_patient_publisher(testing=True)
            
            self.logger.info("Dependencies initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dependencies: {str(e)}")
            raise
    
    def get_total_count(self) -> int:
        """Get total number of patients in the database"""
        try:
            with self.SessionLocal() as db:
                # Count active patients (not soft deleted)
                count = db.query(self.func.count(self.Patient.id)).filter(
                    self.Patient.isDeleted == 0
                ).scalar()
                
                self.logger.info(f"Found {count} active patients in database")
                return count
                
        except Exception as e:
            self.logger.error(f"Error getting patient count: {str(e)}")
            raise
    
    def fetch_batch(self, offset: int, limit: int) -> List[Any]:
        """Fetch a batch of patients from the database"""
        try:
            with self.SessionLocal() as db:
                patients = db.query(self.Patient).filter(
                    self.Patient.isDeleted == 0
                ).order_by(self.Patient.id).offset(offset).limit(limit).all()
                
                self.logger.debug(f"Fetched {len(patients)} patients from offset {offset}")
                return patients
                
        except Exception as e:
            self.logger.error(f"Error fetching patient batch: {str(e)}")
            raise
    
    def process_item(self, patient) -> bool:
        """Process a single patient - emit PATIENT_CREATED event"""
        try:
            patient_id = patient.id
            
            # Check if patient already exists in target (if enabled)
            if self.check_target and self._patient_exists_in_target(patient_id):
                self.logger.info(f"Patient {patient_id} already exists in target - skipping")
                return False  # Skipped, not an error
            
            # Convert patient model to dictionary
            patient_data = self._patient_to_dict(patient)
            
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would emit PATIENT_CREATED for patient {patient_id} ({patient.name})")
                self.logger.debug(f"Patient data: {patient_data}")
                return True
            
            # Emit PATIENT_CREATED event
            success = self.publisher.publish_patient_created(
                patient_id=patient_id,
                patient_data=patient_data,
                created_by="sync_script"
            )
            
            if success:
                self.logger.info(f"Emitted PATIENT_CREATED event for patient {patient_id} ({patient.name})")
                return True
            else:
                self.logger.error(f"Failed to emit PATIENT_CREATED event for patient {patient_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing patient {getattr(patient, 'id', 'unknown')}: {str(e)}")
            raise
    
    def _patient_to_dict(self, patient) -> Dict[str, Any]:
        """Convert patient model to dictionary for messaging"""
        try:
            patient_dict = {}
            
            # Get all patient attributes
            for column in patient.__table__.columns:
                value = getattr(patient, column.name)
                
                # Convert datetime objects to ISO format strings
                if hasattr(value, 'isoformat'):
                    patient_dict[column.name] = value.isoformat()
                else:
                    patient_dict[column.name] = value
            
            return patient_dict
            
        except Exception as e:
            self.logger.error(f"Error converting patient to dict: {str(e)}")
            return {}
    
    def _patient_exists_in_target(self, patient_id: int) -> bool:
        """
        Check if patient already exists in target service
        This is optional and requires target service URL
        """
        if not self.target_service_url:
            return False
        
        try:
            import requests
            
            # Make API call to check if patient exists
            response = requests.get(
                f"{self.target_service_url}/api/patients/{patient_id}",
                timeout=5
            )
            
            # If patient exists (200 OK), skip it
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                self.logger.warning(f"Unexpected response checking patient {patient_id}: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            self.logger.warning(f"Error checking if patient {patient_id} exists in target: {str(e)}")
            # If we can't check, assume it doesn't exist
            return False
    
    def run_with_filters(self, patient_ids: Optional[List[int]] = None,
                        created_after: Optional[str] = None,
                        created_before: Optional[str] = None):
        """
        Run script with additional filters
        
        Args:
            patient_ids: List of specific patient IDs to process
            created_after: Only process patients created after this date (ISO format)
            created_before: Only process patients created before this date (ISO format)
        """
        if patient_ids or created_after or created_before:
            self.logger.info("Running with custom filters:")
            if patient_ids:
                self.logger.info(f"  - Patient IDs: {patient_ids}")
            if created_after:
                self.logger.info(f"  - Created after: {created_after}")
            if created_before:
                self.logger.info(f"  - Created before: {created_before}")
        
        # Override methods to apply filters
        original_get_total_count = self.get_total_count
        original_fetch_batch = self.fetch_batch
        
        def filtered_get_total_count():
            try:
                with self.SessionLocal() as db:
                    query = db.query(self.func.count(self.Patient.id)).filter(
                        self.Patient.isDeleted == 0
                    )
                    
                    if patient_ids:
                        query = query.filter(self.Patient.id.in_(patient_ids))
                    
                    if created_after:
                        from datetime import datetime
                        date_after = datetime.fromisoformat(created_after)
                        query = query.filter(self.Patient.createdDate >= date_after)
                    
                    if created_before:
                        from datetime import datetime
                        date_before = datetime.fromisoformat(created_before)
                        query = query.filter(self.Patient.createdDate <= date_before)
                    
                    return query.scalar()
            except Exception as e:
                self.logger.error(f"Error getting filtered patient count: {str(e)}")
                raise
        
        def filtered_fetch_batch(offset: int, limit: int):
            try:
                with self.SessionLocal() as db:
                    query = db.query(self.Patient).filter(
                        self.Patient.isDeleted == 0
                    )
                    
                    if patient_ids:
                        query = query.filter(self.Patient.id.in_(patient_ids))
                    
                    if created_after:
                        from datetime import datetime
                        date_after = datetime.fromisoformat(created_after)
                        query = query.filter(self.Patient.createdDate >= date_after)
                    
                    if created_before:
                        from datetime import datetime
                        date_before = datetime.fromisoformat(created_before)
                        query = query.filter(self.Patient.createdDate <= date_before)
                    
                    return query.order_by(self.Patient.id).offset(offset).limit(limit).all()
            except Exception as e:
                self.logger.error(f"Error fetching filtered patient batch: {str(e)}")
                raise
        
        # Temporarily override methods
        self.get_total_count = filtered_get_total_count
        self.fetch_batch = filtered_fetch_batch
        
        try:
            self.run()
        finally:
            # Restore original methods
            self.get_total_count = original_get_total_count
            self.fetch_batch = original_fetch_batch


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description='Emit PATIENT_CREATED events for existing patients')
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Run in dry-run mode (no actual events emitted)')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Number of patients to process per batch (default: 100)')
    parser.add_argument('--check-target', action='store_true',
                       help='Check if patients already exist in target service')
    parser.add_argument('--target-url', type=str,
                       help='Target service URL for duplicate checking')
    parser.add_argument('--patient-ids', type=str,
                       help='Comma-separated list of specific patient IDs to process')
    parser.add_argument('--created-after', type=str,
                       help='Only process patients created after this date (ISO format)')
    parser.add_argument('--created-before', type=str,
                       help='Only process patients created before this date (ISO format)')
    
    args = parser.parse_args()
    
    # Parse patient IDs if provided
    patient_ids = None
    if args.patient_ids:
        try:
            patient_ids = [int(pid.strip()) for pid in args.patient_ids.split(',')]
        except ValueError:
            print("Error: Invalid patient IDs format. Use comma-separated integers.")
            sys.exit(1)
    
    try:
        # Create and run the script
        script = PatientSyncScript(
            dry_run=args.dry_run,
            batch_size=args.batch_size,
            check_target=args.check_target,
            target_service_url=args.target_url
        )
        
        if patient_ids or args.created_after or args.created_before:
            script.run_with_filters(
                patient_ids=patient_ids,
                created_after=args.created_after,
                created_before=args.created_before
            )
        else:
            script.run()
            
    except KeyboardInterrupt:
        print("Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Script failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
