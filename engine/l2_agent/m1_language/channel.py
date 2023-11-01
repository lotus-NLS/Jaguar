from pyutils import Countdown
from .channel_interface import ChannelInterface
from .language_types import Entry, SpeakerStaff
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

    def try_remote_entity(self, entity : LingualEntity):
        try:
            self.members.remove(entity)
        except:
            pass

    # ------------------------------
    # Other

    def broadcast(self, entry : Entry):
        for member in self.members:
            member.process_partial_entry(partial_entry=entry)