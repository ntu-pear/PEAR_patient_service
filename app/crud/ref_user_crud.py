import json
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from typing import Optional, Tuple, List
import logging
import math
from ..models.ref_userconfig_model import RefUserConfig
from ..models.processed_events_model import ProcessedEvent
from ..schemas.ref_userconfig import refUserConfigCreate, refUserConfigUpdate
from ..services.idempotency_service import IdempotencyService

logger = logging.getLogger(__name__)


def create_ref_userconfig(
        db: Session,
        userconfig: refUserConfigCreate,
        correlation_id: str,
        created_by: str
        ) -> Tuple[RefUserConfig, bool]:
    """
    Create a new user configuration with idempotency protection.
    Args:
        db: Database session
        userconfig: User configuration data to create
        correlation_id: Correlation ID from outbox service for deduplication
        created_by: User/service creating the user configuration

    Returns:
        Tuple of (RefUserConfig, was_duplicate: bool)

    Raises:
        ValueError: If configuration with same ID already exists (business logic error)
        Exception: For database or other errors
    """
    def create_operation():
            # Check if userconfig already exists - this is a business rule violation for CREATE
            existing = db.query(RefUserConfig).filter(RefUserConfig.UserConfigID == userconfig.UserConfigId).first()
            if existing:
                raise ValueError(f"UserConfig with ID {userconfig.UserConfigId} already exists. Use update operation instead.")

            logger.info(f"Creating new user config {userconfig.UserConfigId}")

            # Use raw SQL for IDENTITY INSERT to handle specific ID
            query = text("""
                SET IDENTITY_INSERT [REF_USERCONFIG] ON;

                INSERT INTO [REF_USERCONFIG] (
                    UserConfigID, configBlob, modifiedDate, modifiedById
                ) VALUES (
                    :UserConfigID, :configBlob, :modifiedDate, :modifiedById
                );

                SET IDENTITY_INSERT [REF_USERCONFIG] OFF;
            """)

            params = {
                "UserConfigID": userconfig.UserConfigId,
                "configBlob": json.dumps(userconfig.configBlob),
                "modifiedDate": userconfig.modifiedDate,
                "modifiedById": created_by,
            }

            db.execute(query, params)
            db.flush()

            # Return the created user config
            created_userconfig = db.query(RefUserConfig).filter(RefUserConfig.UserConfigID == userconfig.UserConfigId).first()
            if not created_userconfig:
                raise Exception(f"Failed to create user config {userconfig.UserConfigId}")

            return created_userconfig

    # Use IdempotencyService for deduplication
    try:
        result, was_duplicate = IdempotencyService.process_idempotent(
            db=db,
            correlation_id=correlation_id,
            event_type="USERCONFIG_CREATED",
            aggregate_id=str(userconfig.UserConfigId),
            processed_by=f"patient_service_{created_by}",
            operation=create_operation
        )

        if was_duplicate:
            # Return existing user config for duplicate events
            existing_userconfig = db.query(RefUserConfig).filter(RefUserConfig.UserConfigID == userconfig.UserConfigId).first()
            logger.info(f"Duplicate create event for user config {userconfig.UserConfigId}, returning existing")
            return existing_userconfig, True

        db.commit()
        logger.info(f"Successfully created user config {userconfig.UserConfigId}")
        return result, False

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user config {userconfig.UserConfigId}: {str(e)}")
        raise


def update_ref_userconfig(
    db: Session,
    userconfig_id: str,
    userconfig_update: refUserConfigUpdate,
    correlation_id: str,
    skip_duplicate_check: bool = False
) -> Tuple[Optional[RefUserConfig], bool]:
    """
    Update an existing user config with idempotency protection.

    Args:
        db: Database session
        userconfig_id: ID of user config to update
        userconfig_update: Fields to update (includes modifiedDate and modifiedById)
        correlation_id: Correlation ID from outbox service for deduplication
        skip_duplicate_check: If True, bypass idempotency check (for sync events)

    Returns:
        Tuple of (RefUserConfig or None, was_duplicate: bool)
        None if user config not found

    Raises:
        Exception: For database or other errors
    """
    def update_operation():
        # Find the user config to update
        db_userconfig = db.query(RefUserConfig).filter(
            RefUserConfig.UserConfigID == userconfig_id
        ).first()

        if not db_userconfig:
            logger.warning(f"UserConfig {userconfig_id} not found for update")
            return None

        logger.debug(f"Updating user config {userconfig_id}")

        # Update only the fields that were provided
        update_data = userconfig_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_userconfig, field) and field != 'UserConfigId':  # Never update ID
                if field == 'configBlob' and isinstance(value, dict):
                    value = json.dumps(value)
                setattr(db_userconfig, field, value)
            

        db.flush()
        return db_userconfig

    # Use IdempotencyService for deduplication (unless skipped for sync events)
    try:
        if skip_duplicate_check:
            logger.info(f"Skipping duplicate check for userconfig {userconfig_id} (sync event)")
            # Execute update directly without idempotency check
            result = update_operation()
            was_duplicate = False

            # Still record the event for tracking, but don't check for duplicates
            try:
                IdempotencyService.record_processed_event(
                    db=db,
                    correlation_id=correlation_id,
                    event_type="USERCONFIG_UPDATED",
                    aggregate_id=str(userconfig_id),
                    processed_by=f"patient_service_{userconfig_update.modifiedById}_sync"
                )
            except Exception as e:
                logger.warning(f"Failed to record sync event (non-critical): {str(e)}")
        else:
            result, was_duplicate = IdempotencyService.process_idempotent(
                db=db,
                correlation_id=correlation_id,
                event_type="USERCONFIG_UPDATED",
                aggregate_id=str(userconfig_id),
                processed_by=f"patient_service_{userconfig_update.modifiedById}",
                operation=update_operation
            )

        if was_duplicate:
            # Return current state for duplicate events
            existing_userconfig = db.query(RefUserConfig).filter(
                RefUserConfig.UserConfigID == userconfig_id
            ).first()
            logger.info(f"Duplicate update event for userconfig {userconfig_id}, returning current state")
            return existing_userconfig, True

        if result is None:
            logger.warning(f"UserConfig {userconfig_id} not found for update")
            db.commit()  # Commit the idempotency record even if userconfig not found
            return None, False

        db.commit()
        logger.debug(f"Successfully updated userconfig {userconfig_id}")
        return result, False

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating userconfig {userconfig_id}: {str(e)}")
        raise


def get_idempotency_stats(db: Session) -> dict:
    """Get statistics about processed events for monitoring."""
    return IdempotencyService.get_processing_stats(db)

def cleanup_old_processed_events(db: Session, older_than_days: int = 30) -> int:
    """Clean up old processed events - should be run periodically."""
    return IdempotencyService.cleanup_old_events(db, older_than_days)


def is_event_already_processed(db: Session, correlation_id: str) -> bool:
    """Check if a specific correlation_id was already processed."""
    return IdempotencyService.is_already_processed(db, correlation_id)
