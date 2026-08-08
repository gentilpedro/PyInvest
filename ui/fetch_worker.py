import queue
import threading

from app.use_cases.fetch_fiis import FetchFiisUseCase


class FetchFiisWorker(threading.Thread):
    """Runs the (blocking, Selenium-based) fetch off the Tk main thread.

    Results are handed back through a queue instead of direct callbacks
    because Tkinter widgets may only be touched from the main thread.
    """

    def __init__(self, result_queue: "queue.Queue"):
        super().__init__(daemon=True)
        self.result_queue = result_queue

    def run(self):
        try:
            df = FetchFiisUseCase().execute()
        except Exception as exc:
            self.result_queue.put(("error", str(exc)))
        else:
            self.result_queue.put(("ok", df))
