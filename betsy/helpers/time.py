from datetime import datetime

class TimeProvider:
    @staticmethod
    def now():
        return datetime.now()
