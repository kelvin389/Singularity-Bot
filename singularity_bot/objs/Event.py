from .User import User
import discord

class Event:
    occurence: str
    users: list[User] # all users including the host (who is always first in the list)
    embed: discord.Embed

    def __init__(self, occurence, users, embed):
        self.occurence = occurence
        self.users = users
        self.embed = embed
        self.update_embed_statuses()

    # construct the status part of the embed
    def update_embed_statuses(self):
        embed_str = ''

        self.embed.remove_field(0) 

        for u in self.users:
            embed_str += f'{u.emoji}{u.id_str} {u.note}\n'
        self.embed.add_field(name="Participants", value=embed_str, inline=True)