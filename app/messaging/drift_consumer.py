import logging
import threading
import json
import uuid
from typing import Dict, Any, Optional
from contextlib import contextmanager

from .rabbitmq_client import RabbitMQClient
from .producer_manager import get_producer_manager

logger = logging.getLogger(__name__)


class DriftConsumer:
    """
    Consumer for drift detection notifications from reconciliation service.
    
    Handles drift by republishing UPDATE sync events for all entity types.
    Since we use soft deletes, there's no need for separate DELETE handlers.
    """
    
    def __init__(self):
        self.client = RabbitMQClient("patient-drift-consumer")
        self.drift_queue = "reconciliation.drift.detected"
        self.shutdown_event = None
        self.is_consuming = False
        
        # Import dependencies
        from app.database import SessionLocal
        
        self.SessionLocal = SessionLocal
        self.producer_manager = get_producer_manager()
        self.exchange = 'patient.updates'
        
        # Import models
        from app.models.patient_model import Patient
        from app.models.patient_medication_model import PatientMedication
        
        self.Patient = Patient
        self.PatientMedication = PatientMedication
    
    @contextmanager
    def get_db_session(self):
        """Context manager for database sessions with proper cleanup"""
        db = self.SessionLocal()
        try:
            yield db
        except Exception as e:
            logger.error(f"Rolling back session due to error: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def _flush_logs(self):
        """Force flush all log handlers"""
        try:
            for handler in logging.getLogger().handlers:
                handler.flush()
            for handler in logger.handlers:
                handler.flush()
        except Exception:
            pass
    
    def set_shutdown_event(self, shutdown_event: threading.Event):
        """Set the shutdown event for graceful shutdown"""
        self.shutdown_event = shutdown_event
        if self.client:
            self.client.set_shutdown_event(shutdown_event)
    
    def setup_consumer(self):
        """Set up consumer to listen to drift detection queue"""
        try:
            self.client.connect()
            
            self.client.channel.exchange_declare(
                exchange='reconciliation.events',
                exchange_type='topic',
                durable=True
            )
            
            self.client.consume(self.drift_queue, self._handle_message_wrapper)
            logger.info(f"Drift consumer set up for queue: {self.drift_queue}")
            
        except Exception as e:
            logger.error(f"Failed to setup drift consumer: {str(e)}")
            raise
    
    def start_consuming(self):
        """Start consuming messages"""
        try:
            self.setup_consumer()
            logger.info("Starting drift consumer...")
            self.is_consuming = True
            self.client.start_consuming()
        except Exception as e:
            logger.error(f"Error starting drift consumer: {str(e)}")
            raise
        finally:
            self.is_consuming = False
    
    def stop(self):
        """Stop the consumer gracefully"""
        logger.info("Stopping drift consumer...")
        self.is_consuming = False
        if self.client:
            self.client.stop_consuming()
    
    def _handle_message_wrapper(self, message: Dict[str, Any]) -> bool:
        """Wrapper for message handling with proper acknowledgment logic"""
        try:
            record_type = message.get('data', {}).get('record_type', 'UNKNOWN')
            record_id = message.get('data', {}).get('record_id', 'UNKNOWN')
            logger.debug(f"RECEIVED DRIFT: type={record_type}, id={record_id}")
            
            if self.shutdown_event and self.shutdown_event.is_set():
                logger.info("Shutdown signal received")
                return False
            
            success = self._process_drift_message(message)
            self._flush_logs()
            
            return success
                
        except Exception as e:
            logger.error(f"Fatal error in message wrapper: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self._flush_logs()
            return False
    
    def _process_drift_message(self, message: Dict[str, Any]) -> bool:
        """Process drift detection message"""
        try:
            message_data = self._parse_message(message)
            if not message_data:
                return False
            
            record_type = message_data['record_type']
            record_id = message_data['record_id']
            drift_type = message_data.get('drift_type', 'unknown')
            
            logger.info(f"Processing drift: {record_type} id={record_id} type={drift_type}")
            
            # Map record types to handlers
            handlers = {
                "patient": (self.Patient, self._publish_patient_sync),
                "patient_medication": (self.PatientMedication, self._publish_medication_sync),
            }
            
            handler_info = handlers.get(record_type)
            if not handler_info:
                logger.warning(f"Unknown record_type: {record_type}")
                return False
            
            model_class, publish_func = handler_info
            
            # Fetch the record (including soft-deleted ones for sync)
            with self.get_db_session() as db:
                # Determine the ID column name based on the model
                if record_type == "patient":
                    record = db.query(model_class).filter(
                        model_class.id == record_id
                    ).first()
                elif record_type == "patient_medication":
                    record = db.query(model_class).filter(
                        model_class.Id == record_id
                    ).first()
                
                if not record:
                    logger.warning(f"{record_type} {record_id} not found in source - skipping sync")
                    return True  # Acknowledge - nothing to sync
                
                # Publish sync event with complete data
                return publish_func(record)
            
        except Exception as e:
            logger.error(f"Error processing drift message: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _parse_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse and validate message structure"""
        try:
            message_data = message.get('data', {})
            
            required_fields = ['record_type', 'record_id']
            for field in required_fields:
                if field not in message_data:
                    logger.error(f"Missing required field '{field}'")
                    return None
            
            return message_data
            
        except Exception as e:
            logger.error(f"Failed to parse message: {str(e)}")
            return None
    
    # ========================
    # RECONCILER WILL TRIGGER THESE SYNC PUBLISHERS
    # All use UPDATE event type with "new_data" field
    # ========================
    
    def _publish_patient_sync(self, patient) -> bool:
        """Publish patient sync event (UPDATE)"""
        try:
            correlation_id = str(uuid.uuid4())
            
            # Complete entity data in new_data
            entity_data = {
                "id": patient.id,
                "name": patient.name,
                "nric": patient.nric,
                "address": patient.address,
                "tempAddress": patient.tempAddress,
                "homeNo": patient.homeNo,
                "handphoneNo": patient.handphoneNo,
                "gender": patient.gender,
                "dateOfBirth": patient.dateOfBirth.isoformat() if patient.dateOfBirth else None,
                "isApproved": patient.isApproved,
                "preferredName": patient.preferredName,
                "preferredLanguageId": patient.preferredLanguageId,
                "updateBit": patient.updateBit,
                "autoGame": patient.autoGame,
                "startDate": patient.startDate.isoformat() if patient.startDate else None,
                "endDate": patient.endDate.isoformat() if patient.endDate else None,
                "isActive": patient.isActive,
                "isRespiteCare": patient.isRespiteCare,
                "privacyLevel": patient.privacyLevel,
                "terminationReason": patient.terminationReason,
                "inActiveReason": patient.inActiveReason,
                "inActiveDate": patient.inActiveDate.isoformat() if patient.inActiveDate else None,
                "profilePicture": patient.profilePicture,
                "createdDate": patient.createdDate.isoformat() if patient.createdDate else None,
                "modifiedDate": patient.modifiedDate.isoformat() if patient.modifiedDate else None,
                "CreatedById": patient.CreatedById,
                "ModifiedById": patient.ModifiedById,
                "isDeleted": patient.isDeleted
            }
            
            message = {
                "correlation_id": correlation_id,
                "event_type": "PATIENT_UPDATED",
                "patient_id": patient.id,
                "old_data": {},
                "new_data": entity_data,
                "changes": {},
                "modified_by": patient.ModifiedById or "drift_reconciliation",
                "modified_by_name": "Drift Reconciliation",
                "timestamp": patient.modifiedDate.isoformat() if patient.modifiedDate else None,
                "is_sync_event": True,
                "sync_reason": "drift_detected"
            }
            
            success = self.producer_manager.publish(
                self.exchange, 
                "patient.updated.sync", 
                message
            )
            
            if success:
                logger.info(f"Published patient sync for id={patient.id}")
            return success
            
        except Exception as e:
            logger.error(f"Error publishing patient sync: {str(e)}")
            return False

    def _publish_medication_sync(self, medication) -> bool:
        """Publish patient medication sync event (UPDATE)"""
        try:
            correlation_id = str(uuid.uuid4())
            
            entity_data = {
                "Id": medication.Id,
                "PatientId": medication.PatientId,
                "PrescriptionListId": medication.PrescriptionListId,
                "AdministerTime": medication.AdministerTime,
                "Dosage": medication.Dosage,
                "Instruction": medication.Instruction,
                "StartDate": medication.StartDate.isoformat() if medication.StartDate else None,
                "EndDate": medication.EndDate.isoformat() if medication.EndDate else None,
                "PrescriptionRemarks": medication.PrescriptionRemarks,
                "IsDeleted": medication.IsDeleted,
                "CreatedDateTime": medication.CreatedDateTime.isoformat() if medication.CreatedDateTime else None,
                "UpdatedDateTime": medication.UpdatedDateTime.isoformat() if medication.UpdatedDateTime else None,
                "CreatedById": medication.CreatedById,
                "ModifiedById": medication.ModifiedById
            }
            
            message = {
                "correlation_id": correlation_id,
                "event_type": "PATIENT_MEDICATION_UPDATED",
                "medication_id": medication.Id,
                "patient_id": medication.PatientId,
                "old_data": {},
                "new_data": entity_data,
                "changes": {},
                "modified_by": medication.ModifiedById or "drift_reconciliation",
                "modified_by_name": "Drift Reconciliation",
                "timestamp": medication.UpdatedDateTime.isoformat() if medication.UpdatedDateTime else None,
                "is_sync_event": True,
                "sync_reason": "drift_detected"
            }
            
            success = self.producer_manager.publish(
                self.exchange,
                "patient.medication.updated.sync",
                message
            )
            
            if success:
                logger.info(f"Published medication sync for id={medication.Id}")
            return success
            
        except Exception as e:
            logger.error(f"Error publishing medication sync: {str(e)}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for monitoring"""
        try:
            return {
                "status": "healthy",
                "service": "drift_consumer",
                "is_consuming": self.is_consuming,
                "queue": self.drift_queue,
                "rabbitmq_connected": self.client.is_connected if self.client else False
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def close(self):
        """Close connections"""
        if self.client:
            self.client.close()
            logger.info("Drift consumer connections closed")
