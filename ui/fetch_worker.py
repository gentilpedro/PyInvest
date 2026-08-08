import queue
import threading
from typing import Callable

import pandas as pd


class FetchWorker(threading.Thread):
    """Runs a (blocking, Selenium-based) fetch off the Tk main thread.

    Results are handed back through a queue instead of direct callbacks
    because Tkinter widgets may only be touched from the main thread.
    """

    def __init__(self, fetch_callable: Callable[[], pd.DataFrame], result_queue: "queue.Queue"):
        super().__init__(daemon=True)
        self.fetch_callable = fetch_callable
        self.result_queue = result_queue

    def run(self):
        try:
            df = self.fetch_callable()
        except Exception as exc:
            self.result_queue.put(("error", str(exc)))
        else:
            self.result_queue.put(("ok", df))
