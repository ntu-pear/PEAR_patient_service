import sys
import os
import argparse
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from .base_script import BaseScript

class PatientMedicationSyncScript(BaseScript):
    """
    Script to emit PATIENT_MEDICATION_CREATED events for existing patient medications in the database
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
            from sqlalchemy.orm import sessionmaker, joinedload
            from sqlalchemy import create_engine, func
            from database import get_database_url
            from app.models.patient_medication_model import PatientMedication
            from app.models.patient_prescription_list_model import PatientPrescriptionList
            
            # Import messaging dependencies  
            from messaging.patient_medication_publisher import get_patient_medication_publisher
            
            # Set up database
            engine = create_engine(get_database_url())
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            self.PatientMedication = PatientMedication
            self.PatientPrescriptionList = PatientPrescriptionList
            self.func = func
            self.joinedload = joinedload
            
            # Set up messaging
            self.publisher = get_patient_medication_publisher(testing=True)
            
            self.logger.info("Dependencies initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dependencies: {str(e)}")
            raise
    
    def get_total_count(self) -> int:
        """Get total number of patient medications in the database"""
        try:
            with self.SessionLocal() as db:
                # Count active patient medications (not soft deleted)
                count = db.query(self.func.count(self.PatientMedication.Id)).filter(
                    self.PatientMedication.IsDeleted == '0'
                ).scalar()
                
                self.logger.info(f"Found {count} active patient medications in database")
                return count
                
        except Exception as e:
            self.logger.error(f"Error getting patient medication count: {str(e)}")
            raise
    
    def fetch_batch(self, offset: int, limit: int) -> List[Any]:
        """Fetch a batch of patient medications from the database WITH prescription names"""
        try:
            with self.SessionLocal() as db:
                # IMPORTANT: Load medications WITH prescription list relationship
                medications = db.query(self.PatientMedication).options(
                    self.joinedload(self.PatientMedication.prescription_list)
                ).filter(
                    self.PatientMedication.IsDeleted == '0'
                ).order_by(self.PatientMedication.Id).offset(offset).limit(limit).all()
                
                self.logger.debug(f"Fetched {len(medications)} patient medications from offset {offset}")
                
                # Debug: Log prescription name loading
                for med in medications:
                    if hasattr(med, 'prescription_list') and med.prescription_list:
                        self.logger.debug(f"Medication {med.Id}: Prescription name loaded = '{med.prescription_list.Value}'")
                    else:
                        self.logger.warning(f"Medication {med.Id}: No prescription name loaded")
                
                return medications
                
        except Exception as e:
            self.logger.error(f"Error fetching patient medication batch: {str(e)}")
            raise
    
    def process_item(self, medication) -> bool:
        """Process a single patient medication - emit PATIENT_MEDICATION_CREATED event"""
        try:
            medication_id = medication.Id
            patient_id = medication.PatientId
            
            # Check if medication already exists in target (if enabled)
            if self.check_target and self._medication_exists_in_target(medication_id):
                self.logger.info(f"Patient medication {medication_id} already exists in target - skipping")
                return False  # Skipped, not an error
            
            # Convert medication model to dictionary WITH prescription name
            medication_data = self._medication_to_dict_with_prescription_name(medication)
            
            # Debug: Log the prescription name
            prescription_name = medication_data.get('PrescriptionName')
            if prescription_name:
                self.logger.info(f"Medication {medication_id}: Prescription name = '{prescription_name}'")
            else:
                self.logger.warning(f"Medication {medication_id}: No prescription name found!")
            
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would emit PATIENT_MEDICATION_CREATED for medication {medication_id} (Patient: {patient_id})")
                self.logger.debug(f"Medication data: {medication_data}")
                return True
            
            # Emit PATIENT_MEDICATION_CREATED event
            success = self.publisher.publish_patient_medication_created(
                medication_id=medication_id,
                patient_id=patient_id,
                medication_data=medication_data,
                created_by="sync_script"
            )
            
            if success:
                self.logger.info(f"Emitted PATIENT_MEDICATION_CREATED event for medication {medication_id} (Patient: {patient_id}) with prescription '{prescription_name}'")
                return True
            else:
                self.logger.error(f"Failed to emit PATIENT_MEDICATION_CREATED event for medication {medication_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing patient medication {getattr(medication, 'Id', 'unknown')}: {str(e)}")
            raise
    
    def _medication_to_dict_with_prescription_name(self, medication) -> Dict[str, Any]:
        """Convert patient medication model to dictionary for messaging, including prescription name"""
        try:
            medication_dict = {}
            
            # Get all medication table attributes
            for column in medication.__table__.columns:
                value = getattr(medication, column.name)
                
                # Convert datetime objects to ISO format strings
                if hasattr(value, 'isoformat'):
                    medication_dict[column.name] = value.isoformat()
                else:
                    medication_dict[column.name] = value
            
            # IMPORTANT: Extract prescription name from the relationship
            prescription_name = None
            if hasattr(medication, 'prescription_list') and medication.prescription_list:
                prescription_name = medication.prescription_list.Value
                self.logger.debug(f"Extracted prescription name from relationship: '{prescription_name}'")
            else:
                # Fallback: Query prescription name directly if relationship not loaded
                prescription_list_id = getattr(medication, 'PrescriptionListId', None)
                if prescription_list_id:
                    prescription_name = self._get_prescription_name_by_id(prescription_list_id)
                    if prescription_name:
                        self.logger.debug(f"Fetched prescription name by ID {prescription_list_id}: '{prescription_name}'")
                    else:
                        self.logger.warning(f"Could not fetch prescription name for ID {prescription_list_id}")
                else:
                    self.logger.warning(f"No PrescriptionListId found for medication {medication.Id}")
            
            # Add prescription name to the dictionary
            medication_dict['PrescriptionName'] = prescription_name
            
            return medication_dict
            
        except Exception as e:
            self.logger.error(f"Error converting medication to dict: {str(e)}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return {}
    
    def _get_prescription_name_by_id(self, prescription_list_id: int) -> Optional[str]:
        """Get prescription name by ID (fallback method)"""
        try:
            with self.SessionLocal() as db:
                prescription = db.query(self.PatientPrescriptionList).filter(
                    self.PatientPrescriptionList.Id == prescription_list_id,
                    self.PatientPrescriptionList.IsDeleted == '0'
                ).first()
                
                if prescription:
                    return prescription.Value
                else:
                    self.logger.warning(f"Prescription with ID {prescription_list_id} not found")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error fetching prescription name for ID {prescription_list_id}: {str(e)}")
            return None
    
    def _medication_to_dict(self, medication) -> Dict[str, Any]:
        """Convert patient medication model to dictionary for messaging (legacy method)"""
        # Use the enhanced method that includes prescription name
        return self._medication_to_dict_with_prescription_name(medication)
    
    def _medication_exists_in_target(self, medication_id: int) -> bool:
        """
        Check if patient medication already exists in target service
        This is optional and requires target service URL
        """
        if not self.target_service_url:
            return False
        
        try:
            import requests
            
            # Make API call to check if medication exists
            response = requests.get(
                f"{self.target_service_url}/api/patient-medications/{medication_id}",
                timeout=5
            )
            
            # If medication exists (200 OK), skip it
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                self.logger.warning(f"Unexpected response checking medication {medication_id}: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            self.logger.warning(f"Error checking if medication {medication_id} exists in target: {str(e)}")
            # If we can't check, assume it doesn't exist
            return False
    
    def run_with_filters(self, medication_ids: Optional[List[int]] = None,
                        patient_ids: Optional[List[int]] = None,
                        created_after: Optional[str] = None,
                        created_before: Optional[str] = None):
        """
        Run script with additional filters
        
        Args:
            medication_ids: List of specific medication IDs to process
            patient_ids: List of specific patient IDs to filter by
            created_after: Only process medications created after this date (ISO format)
            created_before: Only process medications created before this date (ISO format)
        """
        if medication_ids or patient_ids or created_after or created_before:
            self.logger.info("Running with custom filters:")
            if medication_ids:
                self.logger.info(f"  - Medication IDs: {medication_ids}")
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
                    query = db.query(self.func.count(self.PatientMedication.Id)).filter(
                        self.PatientMedication.IsDeleted == '0'
                    )
                    
                    if medication_ids:
                        query = query.filter(self.PatientMedication.Id.in_(medication_ids))
                    
                    if patient_ids:
                        query = query.filter(self.PatientMedication.PatientId.in_(patient_ids))
                    
                    if created_after:
                        date_after = datetime.fromisoformat(created_after)
                        query = query.filter(self.PatientMedication.CreatedDateTime >= date_after)
                    
                    if created_before:
                        date_before = datetime.fromisoformat(created_before)
                        query = query.filter(self.PatientMedication.CreatedDateTime <= date_before)
                    
                    return query.scalar()
            except Exception as e:
                self.logger.error(f"Error getting filtered medication count: {str(e)}")
                raise
        
        def filtered_fetch_batch(offset: int, limit: int):
            try:
                with self.SessionLocal() as db:
                    query = db.query(self.PatientMedication).options(
                        self.joinedload(self.PatientMedication.prescription_list)  # Always load prescription names
                    ).filter(
                        self.PatientMedication.IsDeleted == '0'
                    )
                    
                    if medication_ids:
                        query = query.filter(self.PatientMedication.Id.in_(medication_ids))
                    
                    if patient_ids:
                        query = query.filter(self.PatientMedication.PatientId.in_(patient_ids))
                    
                    if created_after:
                        date_after = datetime.fromisoformat(created_after)
                        query = query.filter(self.PatientMedication.CreatedDateTime >= date_after)
                    
                    if created_before:
                        date_before = datetime.fromisoformat(created_before)
                        query = query.filter(self.PatientMedication.CreatedDateTime <= date_before)
                    
                    return query.order_by(self.PatientMedication.Id).offset(offset).limit(limit).all()
            except Exception as e:
                self.logger.error(f"Error fetching filtered medication batch: {str(e)}")
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
    parser = argparse.ArgumentParser(description='Emit PATIENT_MEDICATION_CREATED events for existing patient medications')
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Run in dry-run mode (no actual events emitted)')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Number of medications to process per batch (default: 100)')
    parser.add_argument('--check-target', action='store_true',
                       help='Check if medications already exist in target service')
    parser.add_argument('--target-url', type=str,
                       help='Target service URL for duplicate checking')
    parser.add_argument('--medication-ids', type=str,
                       help='Comma-separated list of specific medication IDs to process')
    parser.add_argument('--patient-ids', type=str,
                       help='Comma-separated list of specific patient IDs to filter by')
    parser.add_argument('--created-after', type=str,
                       help='Only process medications created after this date (ISO format)')
    parser.add_argument('--created-before', type=str,
                       help='Only process medications created before this date (ISO format)')
    
    args = parser.parse_args()
    
    # Parse medication IDs if provided
    medication_ids = None
    if args.medication_ids:
        try:
            medication_ids = [int(mid.strip()) for mid in args.medication_ids.split(',')]
        except ValueError:
            print("Error: Invalid medication IDs format. Use comma-separated integers.")
            sys.exit(1)
    
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
        script = PatientMedicationSyncScript(
            dry_run=args.dry_run,
            batch_size=args.batch_size,
            check_target=args.check_target,
            target_service_url=args.target_url
        )
        
        if medication_ids or patient_ids or args.created_after or args.created_before:
            script.run_with_filters(
                medication_ids=medication_ids,
                patient_ids=patient_ids,
                created_after=args.created_after,
                created_before=args.created_before
            )
        else:
            script.run()
            
    except KeyboardInterrupt:
        print("\n[WARNING] Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Script failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
