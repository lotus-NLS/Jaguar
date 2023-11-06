from __future__ import annotations

from threading import Lock

from pyutils import Countdown
from .channel_interface import ChannelInterface
from api.types.language import Entry
from .lingual_entity import LingualEntity

# ----------------------------------------------------


class Channel(ChannelInterface):
    def __init__(self):
        super().__init__()
        self.members : list[LingualEntity] = []
        self.speaker_staff : SpeakerStaff = SpeakerStaff()
        self.return_countdown : Countdown = Countdown(time_to_finish=0.5, on_countdown_finish=self.try_release_staff)

    # ------------------------------
    # Staff

    def acquire_staff(self, holder):
        self.speaker_staff.acquire(holder=holder)
        self.return_countdown.relaunch()

    def reset_return_countdown(self):
        self.return_countdown.relaunch()

    def try_release_staff(self):
        try:
            self.speaker_staff.release()
        except:
            pass


    # ------------------------------
    # Update members

    def add_entity(self, entity : LingualEntity):
        self.members.append(entity)
        entity.channel = self

    def try_remote_entity(self, entity : LingualEntity):
        try:
            entity.channel = None
            self.members.remove(entity)
        except:
            pass

    # ------------------------------
    # Other

    def broadcast(self, entry : Entry):
        if not entry.flags is None:
            self.try_release_staff() if entry.flags.is_entry_end else None

        for member in self.members:
            member.process_entry(new_entry=entry)


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
