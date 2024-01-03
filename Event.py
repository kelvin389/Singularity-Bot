from User import User

class Event:
    users: list[User]
    embed_base: str
    embed_str: str

    def __init__(self, users):
        self.users = users

    def update_embed_str(self):
        new_embed_str = ''
        for u in self.users:
            embed_str += f'{u.emoji}{u.id_str} {u.note}\n'
        #embed.add_field(name="Participants", value=embed_str, inline=True)
        # TODO: this function is probably a bad way to do this.
        # maybe have a new var for if Users is updated and automatically all this function
        # whenever embed_str is retrieved if modified
            
    def set_users(self, users):
        self._users = users

    def get_users(self):
        return self._users

    users = property(get_users, set_users)