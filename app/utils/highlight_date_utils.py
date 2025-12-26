# app/utils/date_utils.py
# Business days calculation for cleanup

from datetime import datetime, timedelta

"""
This file contains utility functions for calculating business days. This is used to get the date to perform the cleanup cronjob.

TODO: Need to call API to get holidays and include them in the calculation
"""

def calculate_business_days_ago(business_days: int) -> datetime:
    """
    Calculate the date that is N business days ago.
    Excludes weekends (Saturday, Sunday).
    
    Args:
        business_days: Number of business days to go back
    
    Returns:
        datetime: The date N business days ago
    
    Example:
        If today is Monday Dec 16:
        - 3 business days ago = Wednesday Dec 11 (skips weekend)
    """
    current_date = datetime.now()
    days_counted = 0
    days_back = 0
    
    while days_counted < business_days:
        days_back += 1
        check_date = current_date - timedelta(days=days_back)
        
        # Count only Mon-Fri (0-4)
        if check_date.weekday() < 5:
            days_counted += 1
    
    cutoff_date = current_date - timedelta(days=days_back)
    return cutoff_date