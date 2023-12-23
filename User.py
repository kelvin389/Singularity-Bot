import re

STATUS_HOST = 0
STATUS_UNDECIDED = 1
STATUS_ACCEPTED = 2
STATUS_REJECTED = 3
STATUS_MAYBE = 4

EMOJI_HOST = "👑"
EMOJI_UNDECIDED = "❔"
EMOJI_ACCEPTED = "✅"
EMOJI_REJECTED = "❌"
EMOJI_MAYBE = "🤔"

class User:
    id_str: str
    id: int
    _status: int
    emoji: str
    note: str

    # id_input is an integer containing only the user id when host=True
    # id_input is a string of format <@[id]> when host=False
    def __init__(self, id_input, host=False):
        self.note = ""

        if host:
            self.id = id_input
            self.id_str = "<@" + str(id_input) + ">"
            self.set_status(STATUS_HOST)
        else:
            # extract id from string
            match = re.search(r"<@(\d+)>", id_input)
            self.id = int(match.group(1))
            self.id_str = id_input
            self.set_status(STATUS_UNDECIDED)

    def set_status(self, status):
        self._status = status
        
        if status == STATUS_HOST:
            self.emoji = EMOJI_HOST
        elif status == STATUS_UNDECIDED:
            self.emoji = EMOJI_UNDECIDED
        elif status == STATUS_ACCEPTED:
            self.emoji = EMOJI_ACCEPTED
        elif status == STATUS_REJECTED:
            self.emoji = EMOJI_REJECTED
        elif status == STATUS_MAYBE:
            self.emoji = EMOJI_MAYBE
        else:
            self.emoji = "how"

    def get_status(self):
        return self._status

    status = property(get_status, set_status)