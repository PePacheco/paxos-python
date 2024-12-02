import threading
import time

class TimeoutSemaphore(object):
    def __init__(self, value=1):
        self._semaphore = threading.Semaphore(value)

    def acquire(self, timeout=None):
        """Try to acquire the semaphore within the given timeout."""
        start_time = time.time()
        while True:
            if self._semaphore.acquire(False):  # Non-blocking attempt
                return True
            if timeout is not None and (time.time() - start_time) >= timeout:
                return False
            time.sleep(0.01)  # Sleep briefly to avoid busy-waiting

    def release(self):
        """Release the semaphore."""
        self._semaphore.release()
