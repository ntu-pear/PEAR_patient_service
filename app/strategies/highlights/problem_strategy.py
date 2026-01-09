from typing import Any, Dict, Optional

from sqlalchemy.orm import Session, joinedload

from .base_strategy import HighlightStrategy


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
        # # Get problem name
        # problem_name = getattr(problem_record, 'ProblemName', 
        #                       getattr(problem_record, 'Description', 'Medical problem'))
        
        # # Include severity if available
        # if hasattr(problem_record, 'Severity') and problem_record.Severity:
        #     return f"Problem: {problem_name} ({problem_record.Severity})"
        # else:
        #     return f"Problem: {problem_name}"
        pass
        
    def get_source_remarks(self, db, source_record_id):
        # Implement this after confirming logic
        pass
    
    def get_additional_fields(self, db: Session, source_record_id: int) -> Dict[str, Any]:
        # Implement this after confirming logic with prof
        pass