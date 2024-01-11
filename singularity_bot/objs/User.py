import discord

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
    discord_user: discord.User # discord.py User object. little confusing ; may rename this class in the future
    status_message: discord.Message # the instance of the message containing the status embed sent to this user
    id_str: str
    id: int
    _status: int
    emoji: str
    note: str

    def __init__(self, id, discord_user, init_status):
        self.note = ""
        self.status_message = None
        self.discord_user = discord_user
        self.id = id
        self.id_str = "<@" + str(id) + ">"
        self.status = init_status

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