import logging
from datetime import date
from typing import Optional, Set

import holidays

logger = logging.getLogger(__name__)


class HolidayService:
    """
    Holiday service that uses PyPI's Holiday Library.
    This service is called once every highlight hard deletion cronjob execution to load holidays for the year.
    """
    def __init__(self, country: str = "SG", years: list = None):
        self.country = country
        self._holidays_cache: Optional[Set[date]] = None
        
        if years is None:
            from datetime import datetime
            current_year = datetime.now().year
            self.years = [current_year - 1, current_year, current_year + 1]
        else:
            self.years = years
    
    def _load_holidays(self) -> Set[date]:
        """
        Load holidays from the holidays library.
        Called once per cronjob execution.
        """
        try:
            
            # Get holidays for the specified country and years
            country_holidays = holidays.country_holidays(self.country, years=self.years)
            
            # Extract just the dates
            holiday_dates = set(country_holidays.keys())
            
            logger.info(f"Loaded {len(holiday_dates)} holidays for {self.country} (years: {self.years})")
            return holiday_dates
            
        except ImportError:
            logger.error("'holidays' library not installed. Run: pip install holidays")
            logger.warning("Falling back to weekend-only calculation")
            return set()
        except Exception as e:
            logger.error(f"Error loading holidays: {e}")
            logger.warning("Falling back to weekend-only calculation")
            return set()
    
    def is_holiday(self, check_date: date) -> bool:
        # Load holidays on first call
        if self._holidays_cache is None:
            self._holidays_cache = self._load_holidays()
        
        return check_date in self._holidays_cache
    
    def get_all_holidays(self) -> Set[date]:
        """
        Get all holidays for the configured years.
        """
        if self._holidays_cache is None:
            self._holidays_cache = self._load_holidays()
        
        return self._holidays_cache.copy()


def get_holiday_service(country: str = "SG") -> HolidayService:
    """
    Get a new holiday service instance.
    Since this is called once per cronjob, we don't need singleton.
    
    Returns:
        HolidayService instance
    """
    return HolidayService(country=country)