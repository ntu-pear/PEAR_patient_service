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

class PatientAllocationSyncScript(BaseScript):
    """
    Script to emit PATIENT_ALLOCATION_CREATED events for existing patient allocations in the database
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
            from app.models.patient_allocation_model import PatientAllocation
            from app.models.patient_guardian_model import PatientGuardian
            
            # Import messaging dependencies  
            from messaging.patient_allocation_publisher import get_patient_allocation_publisher
            
            # Set up database
            engine = create_engine(get_database_url())
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            self.PatientAllocation = PatientAllocation
            self.PatientGuardian = PatientGuardian
            self.func = func
            self.joinedload = joinedload
            
            # Set up messaging
            self.publisher = get_patient_allocation_publisher(testing=True)
            
            self.logger.info("Dependencies initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dependencies: {str(e)}")
            raise
    
    def get_total_count(self) -> int:
        """Get total number of patient allocations in the database"""
        try:
            with self.SessionLocal() as db:
                # Count all patient allocations
                count = db.query(self.func.count(self.PatientAllocation.id)).scalar()
                
                self.logger.info(f"Found {count} patient allocations in database")
                return count
                
        except Exception as e:
            self.logger.error(f"Error getting patient allocation count: {str(e)}")
            raise
    
    def fetch_batch(self, offset: int, limit: int) -> List[Any]:
        """Fetch a batch of patient allocations from the database WITH guardian information"""
        try:
            with self.SessionLocal() as db:
                # IMPORTANT: Load allocations WITH guardian relationship
                allocations = db.query(self.PatientAllocation).options(
                    self.joinedload(self.PatientAllocation.guardian)
                ).order_by(self.PatientAllocation.id).offset(offset).limit(limit).all()
                
                self.logger.debug(f"Fetched {len(allocations)} patient allocations from offset {offset}")
                
                # Debug: Log guardian information loading
                for allocation in allocations:
                    if hasattr(allocation, 'guardian') and allocation.guardian:
                        self.logger.debug(f"Allocation {allocation.id}: Guardian loaded = '{allocation.guardian.firstName} {allocation.guardian.lastName}'")
                    else:
                        self.logger.warning(f"Allocation {allocation.id}: No guardian loaded")
                
                return allocations
                
        except Exception as e:
            self.logger.error(f"Error fetching patient allocation batch: {str(e)}")
            raise
    
    def process_item(self, allocation) -> bool:
        """Process a single patient allocation - emit PATIENT_ALLOCATION_CREATED event"""
        try:
            allocation_id = allocation.id
            patient_id = allocation.patientId
            
            # Check if allocation already exists in target (if enabled)
            if self.check_target and self._allocation_exists_in_target(allocation_id):
                self.logger.info(f"Patient allocation {allocation_id} already exists in target - skipping")
                return False  # Skipped, not an error
            
            # Convert allocation model to dictionary WITH guardian information
            allocation_data = self._allocation_to_dict_with_guardian_info(allocation)
            
            # Debug: Log the guardian information
            guardian_user_id = allocation_data.get('guardianApplicationUserId')
            if guardian_user_id:
                self.logger.info(f"Allocation {allocation_id}: Guardian user ID = '{guardian_user_id}'")
            else:
                self.logger.warning(f"Allocation {allocation_id}: No guardian user ID found!")
            
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would emit PATIENT_ALLOCATION_CREATED for allocation {allocation_id} (Patient: {patient_id})")
                self.logger.debug(f"Allocation data: {allocation_data}")
                return True
            
            # Emit PATIENT_ALLOCATION_CREATED event
            success = self.publisher.publish_patient_allocation_created(
                allocation_id=allocation_id,
                patient_id=patient_id,
                allocation_data=allocation_data,
                created_by="sync_script"
            )
            
            if success:
                self.logger.info(f"Emitted PATIENT_ALLOCATION_CREATED event for allocation {allocation_id} (Patient: {patient_id})")
                return True
            else:
                self.logger.error(f"Failed to emit PATIENT_ALLOCATION_CREATED event for allocation {allocation_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing patient allocation {getattr(allocation, 'id', 'unknown')}: {str(e)}")
            raise
    
    def _allocation_to_dict_with_guardian_info(self, allocation) -> Dict[str, Any]:
        """Convert patient allocation model to dictionary for messaging, including guardian information"""
        try:
            allocation_dict = {}
            
            # Get all allocation table attributes
            for column in allocation.__table__.columns:
                value = getattr(allocation, column.name)
                
                # Convert datetime objects to ISO format strings
                if hasattr(value, 'isoformat'):
                    allocation_dict[column.name] = value.isoformat()
                else:
                    allocation_dict[column.name] = value
            
            # IMPORTANT: Extract guardian application user ID from the relationship
            guardian_user_id = None
            if hasattr(allocation, 'guardian') and allocation.guardian:
                guardian_user_id = allocation.guardian.guardianApplicationUserId
                self.logger.debug(f"Extracted guardian user ID from relationship: '{guardian_user_id}'")
            else:
                # Fallback: Query guardian information directly if relationship not loaded
                guardian_id = getattr(allocation, 'guardianId', None)
                if guardian_id:
                    guardian_user_id = self._get_guardian_user_id(guardian_id)
                    if guardian_user_id:
                        self.logger.debug(f"Fetched guardian user ID for guardian {guardian_id}: '{guardian_user_id}'")
                    else:
                        self.logger.warning(f"Could not fetch guardian user ID for guardian {guardian_id}")
                else:
                    self.logger.warning(f"No guardianId found for allocation {allocation.id}")
            
            # Add guardian application user ID to the dictionary
            allocation_dict['guardianApplicationUserId'] = guardian_user_id
            
            return allocation_dict
            
        except Exception as e:
            self.logger.error(f"Error converting allocation to dict: {str(e)}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return {}
    
    def _get_guardian_user_id(self, guardian_id: int) -> Optional[str]:
        """Get guardian application user ID by guardian ID (fallback method)"""
        try:
            with self.SessionLocal() as db:
                guardian = db.query(self.PatientGuardian).filter(
                    self.PatientGuardian.id == guardian_id,
                    self.PatientGuardian.isDeleted == '0'
                ).first()
                
                if guardian:
                    return guardian.guardianApplicationUserId
                else:
                    self.logger.warning(f"Guardian with ID {guardian_id} not found")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error fetching guardian user ID for guardian {guardian_id}: {str(e)}")
            return None
    
    def _allocation_to_dict(self, allocation) -> Dict[str, Any]:
        """Convert patient allocation model to dictionary for messaging (legacy method)"""
        # Use the enhanced method that includes guardian information
        return self._allocation_to_dict_with_guardian_info(allocation)
    
    def _allocation_exists_in_target(self, allocation_id: int) -> bool:
        """
        Check if patient allocation already exists in target service
        This is optional and requires target service URL
        """
        if not self.target_service_url:
            return False
        
        try:
            import requests
            
            # Make API call to check if allocation exists
            response = requests.get(
                f"{self.target_service_url}/api/patient-allocations/{allocation_id}",
                timeout=5
            )
            
            # If allocation exists (200 OK), skip it
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                self.logger.warning(f"Unexpected response checking allocation {allocation_id}: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            self.logger.warning(f"Error checking if allocation {allocation_id} exists in target: {str(e)}")
            # If we can't check, assume it doesn't exist
            return False
    
    def run_with_filters(self, allocation_ids: Optional[List[int]] = None,
                        patient_ids: Optional[List[int]] = None,
                        created_after: Optional[str] = None,
                        created_before: Optional[str] = None):
        """
        Run script with additional filters
        
        Args:
            allocation_ids: List of specific allocation IDs to process
            patient_ids: List of specific patient IDs to filter by
            created_after: Only process allocations created after this date (ISO format)
            created_before: Only process allocations created before this date (ISO format)
        """
        if allocation_ids or patient_ids or created_after or created_before:
            self.logger.info("Running with custom filters:")
            if allocation_ids:
                self.logger.info(f"  - Allocation IDs: {allocation_ids}")
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
                    query = db.query(self.func.count(self.PatientAllocation.id))
                    
                    if allocation_ids:
                        query = query.filter(self.PatientAllocation.id.in_(allocation_ids))
                    
                    if patient_ids:
                        query = query.filter(self.PatientAllocation.patientId.in_(patient_ids))
                    
                    if created_after:
                        date_after = datetime.fromisoformat(created_after)
                        query = query.filter(self.PatientAllocation.createdDate >= date_after)
                    
                    if created_before:
                        date_before = datetime.fromisoformat(created_before)
                        query = query.filter(self.PatientAllocation.createdDate <= date_before)
                    
                    return query.scalar()
            except Exception as e:
                self.logger.error(f"Error getting filtered allocation count: {str(e)}")
                raise
        
        def filtered_fetch_batch(offset: int, limit: int):
            try:
                with self.SessionLocal() as db:
                    query = db.query(self.PatientAllocation).options(
                        self.joinedload(self.PatientAllocation.guardian)  # Always load guardian info
                    )
                    
                    if allocation_ids:
                        query = query.filter(self.PatientAllocation.id.in_(allocation_ids))
                    
                    if patient_ids:
                        query = query.filter(self.PatientAllocation.patientId.in_(patient_ids))
                    
                    if created_after:
                        date_after = datetime.fromisoformat(created_after)
                        query = query.filter(self.PatientAllocation.createdDate >= date_after)
                    
                    if created_before:
                        date_before = datetime.fromisoformat(created_before)
                        query = query.filter(self.PatientAllocation.createdDate <= date_before)
                    
                    return query.order_by(self.PatientAllocation.id).offset(offset).limit(limit).all()
            except Exception as e:
                self.logger.error(f"Error fetching filtered allocation batch: {str(e)}")
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
    parser = argparse.ArgumentParser(description='Emit PATIENT_ALLOCATION_CREATED events for existing patient allocations')
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Run in dry-run mode (no actual events emitted)')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Number of allocations to process per batch (default: 100)')
    parser.add_argument('--check-target', action='store_true',
                       help='Check if allocations already exist in target service')
    parser.add_argument('--target-url', type=str,
                       help='Target service URL for duplicate checking')
    parser.add_argument('--allocation-ids', type=str,
                       help='Comma-separated list of specific allocation IDs to process')
    parser.add_argument('--patient-ids', type=str,
                       help='Comma-separated list of specific patient IDs to filter by')
    parser.add_argument('--created-after', type=str,
                       help='Only process allocations created after this date (ISO format)')
    parser.add_argument('--created-before', type=str,
                       help='Only process allocations created before this date (ISO format)')
    
    args = parser.parse_args()
    
    # Parse allocation IDs if provided
    allocation_ids = None
    if args.allocation_ids:
        try:
            allocation_ids = [int(aid.strip()) for aid in args.allocation_ids.split(',')]
        except ValueError:
            print("Error: Invalid allocation IDs format. Use comma-separated integers.")
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
        script = PatientAllocationSyncScript(
            dry_run=args.dry_run,
            batch_size=args.batch_size,
            check_target=args.check_target,
            target_service_url=args.target_url
        )
        
        if allocation_ids or patient_ids or args.created_after or args.created_before:
            script.run_with_filters(
                allocation_ids=allocation_ids,
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
    finally:
        # Ensure all messages are published before exiting
        print("Shutting down producer manager...")
        from messaging.producer_manager import stop_producer_manager
        stop_producer_manager()
        print("Producer manager stopped. Script complete.")

if __name__ == "__main__":
    main()
