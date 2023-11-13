from datetime import datetime, timedelta
from typing import Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.job import Job
from typing import Optional


from .input_waiter import InputWaiter
# ---------------------------------------------------------

class Countdown:
    def __init__(self, time_to_finish: float = 0.25, on_countdown_finish : Callable[[], None] = lambda *args,**kwargs : None):
        self.initial_time = time_to_finish
        self.scheduler = BackgroundScheduler()
        self.job: Optional[Job] = None
        self.on_countdown_finsh : Callable[[], None] = on_countdown_finish

        self.one_time_lock = InputWaiter()
        self.scheduler.start()


    def relaunch(self):
        try:
            self.job.remove()
        except:
            pass

        self.launch()

    def launch(self):
        run_time = datetime.now() + timedelta(seconds=self.initial_time)
        self.job = self.scheduler.add_job(func=self._release, trigger='date', next_run_time=run_time)

    # Returns when the time has run out
    def finish(self):
        _ = self.one_time_lock.read()


    def _release(self):
        self.one_time_lock.write('open sesame')
        self.on_countdown_finsh()

