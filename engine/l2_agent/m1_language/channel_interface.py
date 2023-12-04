from __future__ import annotations

from threading import Lock

from api import Entry
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


class SpeakerStaff:
    def __init__(self):
        self.lock = Lock()
        self.holder = None

    def acquire(self, holder):
        acquired = self.lock.acquire(blocking=False)  # Try to acquire the lock
        if acquired:
            self.holder = holder
        return acquired

    def release(self):
        self.lock.release()
        self.holder = None

    def current_holder(self):
        return self.holder
