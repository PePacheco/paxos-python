import threading
from datetime import datetime

class TimestampManager:
    _instance = None
    _lock = threading.Lock()

    @staticmethod
    def get_instance():
        """Static method to get the singleton instance."""
        if TimestampManager._instance is None:
            with TimestampManager._lock:
                if TimestampManager._instance is None:
                    TimestampManager._instance = TimestampManager()
        return TimestampManager._instance

    def __init__(self):
        if TimestampManager._instance is not None:
            raise Exception("This class is a singleton! Use get_instance() to access it.")
        self.timestamps = {}
        self.lock = threading.Lock()

    def set_timestamp(self, key, value):
        """Thread-safe method to set a timestamp."""
        with self.lock:
            self.timestamps[key] = value
            print("Set {}: {}".format(key, value))


    def get_timestamp(self, key):
        """Thread-safe method to get a timestamp."""
        with self.lock:
            return self.timestamps.get(key, None)

    def get_time_difference(self, key1, key2):
        """Thread-safe method to calculate the difference between two timestamps."""
        with self.lock:
            t1 = self.timestamps.get(key1)
            t2 = self.timestamps.get(key2)
            if t1 and t2:
                return t2 - t1
            else:
                return None

timestampManager = TimestampManager()