from typing import List
from sqlalchemy.orm import Session
from ..models.social_history_sensitive_mapping_model import SocialHistorySensitiveMapping
from ..schemas.social_history_sensitive_mapping import SocialHistorySensitiveCreate, SocialHistorySensitiveUpdate

def get_all_social_history(db: Session, skip: int = 0, limit: int = 10):
    return db.query(SocialHistorySensitiveMapping).order_by(SocialHistorySensitiveMapping.id).offset(skip).limit(limit).all()

def get_all_sensitive_social_history(db: Session):
    return db.query(SocialHistorySensitiveMapping).filter(SocialHistorySensitiveMapping.isSensitive == True).all()

def get_all_non_sensitive_social_history(db: Session):
    return db.query(SocialHistorySensitiveMapping).filter(SocialHistorySensitiveMapping.isSensitive == False).all()

def create_sensitive_mapping(db: Session, social_history: SocialHistorySensitiveCreate, created_by: str):
    db_sensitive_mapping = SocialHistorySensitiveMapping(**social_history.model_dump(),createdById=created_by,modifiedById=created_by)
    db.add(db_sensitive_mapping)
    db.commit()
    db.refresh(db_sensitive_mapping)
    return db_sensitive_mapping

def update_all_sensitive_mapping(db: Session, social_history_list: List[SocialHistorySensitiveUpdate], modified_by:str):
    social_history_list_names = {item.socialHistoryItem for item in social_history_list}
    social_history_list_sensitive = {item.socialHistoryItem: item.isSensitive for item in social_history_list}
    
    db_sensitive_mapping = db.query(SocialHistorySensitiveMapping).filter(SocialHistorySensitiveMapping.socialHistoryItem.in_(social_history_list_names)).all()
    
    for record in db_sensitive_mapping:
        if record.socialHistoryItem in social_history_list_sensitive:
            record.isSensitive = social_history_list_sensitive[record.socialHistoryItem]
            record.modifiedById = modified_by
    
    db.commit()
    
    for record in db_sensitive_mapping:
        db.refresh(record)
    
    return db_sensitive_mapping
    
def delete_sensitive_mapping(db: Session, social_history_item: str):
    db_sensitive_mapping = db.query(SocialHistorySensitiveMapping).filter(SocialHistorySensitiveMapping.socialHistoryItem == social_history_item).first()
    if db_sensitive_mapping:
        db.delete(db_sensitive_mapping)
        db.commit()
    return db_sensitive_mapping