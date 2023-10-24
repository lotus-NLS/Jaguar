from datetime import datetime, timedelta
from typing import Optional
from apscheduler.job import Job
from apscheduler.schedulers.background import BackgroundScheduler


class Debouncer:
    def __init__(self, debounce_time : float = 0.25, logger=None):
        self.debounce_time = debounce_time
        self.content = ''
        self.logger = logger if logger else print

        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.job :Optional[Job] = None

    def _log_accumulated_content(self):
        self.logger(self.content)

    def add(self, new_msg : str):
        self.content += new_msg

        try:
            self.job.remove()
        except:
            pass

        run_time = datetime.now() + timedelta(seconds=self.debounce_time)
        self.job = self.scheduler.add_job(func=self._log_accumulated_content,trigger='date',next_run_time=run_time)


# this_debounce = Debouncer()
# this_debounce.add('abc')
# this_debounce.add('def')
# time.sleep(2)
# this_debounce.add('new')
#
# time.sleep(0.5)
