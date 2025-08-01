"""
Messaging Scripts Module

This module contains scripts for various messaging operations:

1. **patient_sync_script.py** - Emit PATIENT_CREATED events for existing patients
2. **base_script.py** - Base framework for all messaging scripts

Usage:
    # Run patient sync in dry-run mode
    python run_scripts.py patient-sync --dry-run
    
    # Run patient sync for real  
    python run_scripts.py patient-sync
    
    # Run with custom batch size
    python run_scripts.py patient-sync --batch-size 50
    
    # Run for specific patients only
    python run_scripts.py patient-sync --patient-ids "1,2,3"
    
    # Run with date filters
    python run_scripts.py patient-sync --created-after "2024-01-01"

Testing:
    # Test script setup
    python test_scripts.py
"""

from .base_script import BaseScript
from .patient_sync_script import PatientSyncScript

__all__ = ["BaseScript", "PatientSyncScript"]
