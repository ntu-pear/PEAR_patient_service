class Config:
    class Vital:
        class Temperature:
            MIN_VALUE = 35
            MAX_VALUE = 38
        class SystolicBP:
            MIN_VALUE = 91
            MAX_VALUE = 140
        class DiastolicBP:
            MIN_VALUE = 61
            MAX_VALUE = 90
        class SpO2:
            MIN_VALUE = 95
            MAX_VALUE = 100
        class BloodSugarLevel:
            MIN_VALUE = 6
            MAX_VALUE = 13
        # class BslBeforeMeal:
        #     MIN_VALUE = 6
        #     MAX_VALUE = 10
        # class BslAfterMeal:
        #     MIN_VALUE = 7
        #     MAX_VALUE = 13
        class HeartRate:
            MIN_VALUE = 60
            MAX_VALUE = 100