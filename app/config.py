class Config:
    class Vital:
        class Temperature:
            MIN_VALUE = 30
            MAX_VALUE = 42
        class SystolicBP:
            MIN_VALUE = 60
            MAX_VALUE = 200
        class DiastolicBP:
            MIN_VALUE = 40
            MAX_VALUE = 130
        class SpO2:
            MIN_VALUE = 70
            MAX_VALUE = 100
        class BloodSugarLevel:
            MIN_VALUE = 2
            MAX_VALUE = 30
        # class BslBeforeMeal:
        #     MIN_VALUE = 6
        #     MAX_VALUE = 10
        # class BslAfterMeal:
        #     MIN_VALUE = 7
        #     MAX_VALUE = 13
        class HeartRate:
            MIN_VALUE = 30
            MAX_VALUE = 200