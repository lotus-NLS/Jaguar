from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.job import Job
from typing import Optional


from .input_waiter import InputWaiter
# ---------------------------------------------------------

class Countdown:
    def __init__(self, time_to_finish: float = 0.25):
        self.initial_time = time_to_finish
        self.scheduler = BackgroundScheduler()
        self.job: Optional[Job] = None

        self.one_time_lock = InputWaiter()
        self.scheduler.start()

    def reset(self):
        try:
            self.job.remove()
        except:
            pass

        self.launch()

    def launch(self):
        run_time = datetime.now() + timedelta(seconds=self.initial_time)
        self.job = self.scheduler.add_job(func=self._release, trigger='date', next_run_time=run_time)

    # Returns when the time has run out
    def get(self):
        _ = self.one_time_lock.read()
        # print(f'Temp debug: Countdown has run out')

    def _release(self):
        self.one_time_lock.write('open sesame')

