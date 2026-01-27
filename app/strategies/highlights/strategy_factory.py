from typing import Dict

from .allergy_strategy import AllergyStrategy
from .base_strategy import HighlightStrategy
from .medication_strategy import MedicationStrategy
from .prescription_strategy import PrescriptionStrategy
from .problem_strategy import ProblemStrategy
from .vital_strategy import VitalStrategy


class HighlightStrategyFactory:
    """
    Factory to create and manage highlight strategies.
    """
    
    def __init__(self):
        self._strategies: Dict[str, HighlightStrategy] = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """Register all available strategies"""
        self.register_strategy(VitalStrategy())
        self.register_strategy(AllergyStrategy())
        self.register_strategy(MedicationStrategy())
        self.register_strategy(PrescriptionStrategy())
        self.register_strategy(ProblemStrategy())
        
        # Add more strategies:
        # self.register_strategy(LabStrategy())
    
    def register_strategy(self, strategy: HighlightStrategy):
        """Register a strategy by its type code"""
        self._strategies[strategy.get_type_code()] = strategy
    
    def get_strategy(self, type_code: str) -> HighlightStrategy:
        """Get strategy by type code"""
        strategy = self._strategies.get(type_code)
        if not strategy:
            raise ValueError(f"No strategy found for type: {type_code}")
        return strategy
    
    def has_strategy(self, type_code: str) -> bool:
        """Check if strategy exists for type code"""
        return type_code in self._strategies