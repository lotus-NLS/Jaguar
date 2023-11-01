from .language_types import Entry, SpeakerStaff
from abc import abstractmethod
# ----------------------------------------------------


class ChannelInterface:
    def __init__(self):
        self.speaker_staff : SpeakerStaff = SpeakerStaff()

    # ------------------------------
    # Staff

    @abstractmethod
    def reset_return_countdown(self):
        pass

    @abstractmethod
    def acquire_staff(self, holder):
        pass

    @abstractmethod
    def try_release_staff(self):
        pass

    # ------------------------------
    # Other

    @abstractmethod
    def broadcast(self, entry : Entry):
        pass