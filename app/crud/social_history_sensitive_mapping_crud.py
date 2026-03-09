from typing import List
from sqlalchemy.orm import Session
from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.social_history_sensitive_mapping_model import SocialHistorySensitiveMapping
from ..schemas.social_history_sensitive_mapping import SocialHistorySensitiveCreate, SocialHistorySensitiveUpdate

def get_all_social_history(db: Session):
    return db.query(SocialHistorySensitiveMapping).order_by(SocialHistorySensitiveMapping.id).all()

def get_all_sensitive_social_history(db: Session):
    return db.query(SocialHistorySensitiveMapping).filter(SocialHistorySensitiveMapping.isSensitive == True).all()

def get_all_non_sensitive_social_history(db: Session):
    return db.query(SocialHistorySensitiveMapping).filter(SocialHistorySensitiveMapping.isSensitive == False).all()

def create_sensitive_mapping(db: Session, social_history: SocialHistorySensitiveCreate, created_by: str, user_full_name: str):
    db_sensitive_mapping = SocialHistorySensitiveMapping(**social_history.model_dump(),createdById=created_by,modifiedById=created_by)
    db.add(db_sensitive_mapping)
    db.commit()
    db.refresh(db_sensitive_mapping)

    updated_data_dict = serialize_data(social_history.model_dump())

    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        user_full_name=user_full_name,
        message=f"Created social history sensitive mapping: {db_sensitive_mapping.socialHistoryItem} (Sensitive: {db_sensitive_mapping.isSensitive})",
        table="SocialHistorySensitiveMapping",
        entity_id = db_sensitive_mapping.id,
        original_data = None,
        updated_data = updated_data_dict,
        log_type = "system",
        is_system_config = True,
    )
    return db_sensitive_mapping

def update_all_sensitive_mapping(db: Session, social_history_list: List[SocialHistorySensitiveUpdate], modified_by:str, user_full_name:str):
    social_history_list_names = {item.socialHistoryItem for item in social_history_list}
    social_history_list_sensitive = {item.socialHistoryItem: item.isSensitive for item in social_history_list}
    
    db_sensitive_mapping = db.query(SocialHistorySensitiveMapping).filter(SocialHistorySensitiveMapping.socialHistoryItem.in_(social_history_list_names)).all()

    # capture original data before updates
    original_data_list = []
    
    for record in db_sensitive_mapping:
        try:
            original_data = {
                k: serialize_data(v) for k, v in record.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data = "{}"
        original_data_list.append((record, original_data))
    for record in db_sensitive_mapping:
        if record.socialHistoryItem in social_history_list_sensitive:
            record.isSensitive = social_history_list_sensitive[record.socialHistoryItem]
            record.modifiedById = modified_by
    
    db.commit()
    
    for record in db_sensitive_mapping:
        db.refresh(record)

    # Log each update
    for record, original_data in original_data_list:
        updated_data = {"isSensitive": record.isSensitive, "socialHistoryItem": record.socialHistoryItem}
        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            user_full_name=user_full_name,
            message = f"Updated social history sensitive mapping: {record.socialHistoryItem} (Sensitive: {record.isSensitive})",
            table="SocialHistorySensitiveMapping",
            entity_id = record.socialHistoryItem.id,
            original_data = original_data,
            updated_data = updated_data,
            log_type = "system",
            is_system_config = True,
        )
    
    return db_sensitive_mapping
    
def delete_sensitive_mapping(db: Session, social_history_item: str, modified_by:str, user_full_name:str):
    db_sensitive_mapping = db.query(SocialHistorySensitiveMapping).filter(SocialHistorySensitiveMapping.socialHistoryItem == social_history_item).first()
    if db_sensitive_mapping:
        try:
            original_data = {
                k: serialize_data(v) for k, v in db_sensitive_mapping.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data = "{}"
        db.delete(db_sensitive_mapping)
        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            user_full_name=user_full_name,
            message=f"Deleted social history sensitive mapping: {db_sensitive_mapping.socialHistoryItem}",
            table="SocialHistorySensitiveMapping",
            entity_id = db_sensitive_mapping.id,
            original_data = original_data,
            updated_data = original_data,
            log_type = "system",
            is_system_config = True,
        )
    return db_sensitive_mapping