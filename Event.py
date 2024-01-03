from User import User

class Event:
    users: list[User]
    embed_base: str
    embed_str: str

    def __init__(self, event, users, datetime, timestamp):
        self._event = event
        self._users = users
        self._datetime = datetime
        self._timestamp = timestamp

    def update_embed_str(self):
        new_embed_str = ''
        for u in self.users:
            embed_str += f'{u.emoji}{u.id_str} {u.note}\n'
        #embed.add_field(name="Participants", value=embed_str, inline=True)
        # TODO: this function is probably a bad way to do this.
        # maybe have a new var for if Users is updated and automatically all this function
        # whenever embed_str is retrieved if modified
            
    def set_event(self, event):
        self._event = event

    def get_event(self):
        return self._event

    event = property(get_event, set_event)
            
    def set_users(self, users):
        self._users = users

    def get_users(self):
        return self._users

    users = property(get_users, set_users)


    def set_datetime(self, datetime):
        self._datetime = datetime

    def get_datetime(self):
        return self._datetime

    datetime = property(get_datetime, set_datetime)


    def set_timestamp(self, timestamp):
        self._timestamp = timestamp

    def get_timestamp(self):
        return self._timestamp

    timestamp = property(get_timestamp, set_timestamp)