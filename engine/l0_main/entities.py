from PIL.Image import Image as PILImage
from api import Entry
from typing import Optional
from engine.l5_singletons import Task
# from api import NetworkAddresses
# ----------------------------------------------


class ConsoleUser:
    def send(self, msg : str, image : Optional[PILImage] = None):
        task = Task(new_entries=[Entry.as_user(msg=msg, image=image)])
        raise NotImplementedError


class WebappUserSpoof:
    def send(self, msg : str, image : Optional[PILImage] = None):
        pass

