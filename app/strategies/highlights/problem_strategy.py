from .base_strategy import HighlightStrategy


class ProblemStrategy(HighlightStrategy):
    """Strategy for generating highlights from medical problems (ultra-simplified)"""
    
    def get_type_code(self) -> str:
        """Return type code that matches database"""
        return "PROBLEM"
    
    def should_generate_highlight(self, problem_record) -> bool:
        """
        Check if problem should be highlighted.
        
        CUSTOMIZE THIS based on your needs:
        - Option 1: Highlight all active problems (default)
        - Option 2: Only critical/severe problems
        - Option 3: Specific problem types
        """
        # Option 1: All active problems
        # if hasattr(problem_record, 'Status'):
        #     return problem_record.Status == "Active"
        
        # Option 2: Only critical/severe
        # if hasattr(problem_record, 'Severity'):
        #     return problem_record.Severity in ["Critical", "Severe"]
        
        # Option 3: Specific problem types
        # critical_problems = ["Sepsis", "Stroke", "MI", "Pneumonia"]
        # if hasattr(problem_record, 'ProblemName'):
        #     for critical in critical_problems:
        #         if critical.lower() in problem_record.ProblemName.lower():
        #             return True
        
        # Default: highlight all active
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
        
    def get_source_value(self, db, source_record_id):
        # Implement this after confirming logic
        pass