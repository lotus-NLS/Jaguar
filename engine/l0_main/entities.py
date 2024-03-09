from PIL.Image import Image as PILImage
from api import Entry
from engine.l5_singletons import Response, Task, User
from typing import Optional
# ----------------------------------------------


class ConsoleUser(User):
    def send(self, msg : str, image : Optional[PILImage] = None) -> Response:
        task = Task(new_entries=[Entry.as_user(msg=msg, image=image)])
        return self.io.handle(task=task)


class WebappUserSpoof(User):
    def send(self, msg : str, image : Optional[PILImage] = None):
        pass

