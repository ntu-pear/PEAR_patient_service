import logging
from datetime import date, datetime, timedelta
from typing import Optional

import holidays

logger = logging.getLogger(__name__)

"""
This file contains utility functions for calculating business days. This is used to get the date to perform the cleanup cronjob.

Business days = all days except weekends (Saturday and Sunday) and Singapore Public Holidays.
"""

def calculate_business_days_ago(business_days: int, country: str = "SG") -> datetime:
    """
    Calculate the date that is N business days ago.
    Excludes weekends (Saturday, Sunday) and public holidays.
    
    Returns:
        datetime: The date N business days ago
    
    Example:
        If today is Thursday and you want 3 business days ago:
        - Skips Saturday, Sunday, and public holidays
        - Returns the date 3 business days back
    """
    # Load holidays once at the start
    holidays_set = _load_holidays(country)
    
    current_date = datetime.now()
    days_counted = 0
    days_back = 0
    
    while days_counted < business_days:
        days_back += 1
        check_date = current_date - timedelta(days=days_back)
        
        # Skip weekends (Saturday=5, Sunday=6)
        if check_date.weekday() >= 5:
            continue
        
        # Skip public holidays
        if check_date.date() in holidays_set:
            logger.debug(f"Skipping holiday: {check_date.date()}")
            continue
        
        # This is a valid business day
        days_counted += 1
    
    cutoff_date = current_date - timedelta(days=days_back)
    
    logger.info(
        f"Calculated {business_days} business days ago: {cutoff_date.date()} "
        f"(went back {days_back} calendar days, country: {country})"
    )
    
    return cutoff_date


def _load_holidays(country: str = "SG") -> set:
    """
    Load holidays from the holidays library.
    Called once per execution.
    
    Returns:
        set: Set of holiday dates for the current year
    """
    try:
        
        current_year = datetime.now().year
        
        # Load holidays
        country_holidays = holidays.country_holidays(country, years=current_year)
        holiday_dates = set(country_holidays.keys())
        
        logger.info(f"Loaded {len(holiday_dates)} holidays for {country} (year: {current_year})")
        return holiday_dates
        
    except ImportError:
        logger.error("'holidays' library not installed. Run: pip install holidays")
        logger.warning("Falling back to weekend-only calculation")
        return set()
    except Exception as e:
        logger.error(f"Error loading holidays: {e}")
        logger.warning("Falling back to weekend-only calculation")
        return set()