import logging
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.patient_problem_model import PatientProblem

from .base_strategy import HighlightStrategy

logger = logging.getLogger(__name__)

class ProblemStrategy(HighlightStrategy):
    """Strategy for generating highlights from medical problems"""
    
    def get_type_code(self) -> str:
        """Return type code that matches database"""
        return "PROBLEM"
    
    def should_generate_highlight(self, problem_record, db: Optional[Session] = None) -> bool:
        """
        Check if problem should be highlighted.
        """

        # Default: highlight all recently created or updated problems
        return True
    
    def generate_highlight_text(self, problem_record) -> str:
        """
        Generate readable problem text.
        Shows the problem name/description.
        """
        try:
            # Try to get problem name from loaded relationship
            if hasattr(problem_record, 'problem_list') and problem_record.problem_list:
                problem_name = problem_record.problem_list.ProblemName
                return f"Problem: {problem_name}"
            
            # Fallback to generic message if relationship not loaded
            logger.warning(f"Problem {getattr(problem_record, 'Id', 'unknown')} - problem_list relationship not loaded")
            return "Active problem"
            
        except Exception as e:
            logger.error(f"Error generating problem highlight text: {e}")
            return "Active problem"
        
    def get_source_remarks(self, db, source_record_id):
        try:
            problem = db.query(PatientProblem).filter(
                PatientProblem.Id == source_record_id
            ).first()
            
            if problem:
                return problem.ProblemRemarks
            return None
            
        except Exception as e:
            logger.error(f"Error getting problem source remarks: {e}")
            return None
    
    def get_additional_fields(self, db: Session, source_record_id: int) -> Dict[str, Any]:
        try:
            # Query with problem_list relationship loaded
            problem = db.query(PatientProblem).options(
                joinedload(PatientProblem.problem_list)
            ).filter(
                PatientProblem.Id == source_record_id
            ).first()
            
            if not problem:
                return {}
            
            # Build response with all relevant details
            result = {
                "problem_name": problem.problem_list.ProblemName if problem.problem_list else None,
                "date_of_diagnosis": problem.DateOfDiagnosis.isoformat() if problem.DateOfDiagnosis else None,
                "source_of_information": problem.SourceOfInformation,
                "problem_remarks": problem.ProblemRemarks
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting problem additional fields: {e}")
            return {}