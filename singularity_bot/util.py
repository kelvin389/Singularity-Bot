import json
import re
import datetime
import zoneinfo

from dateutil import relativedelta
import discord.ext.commands.bot as bot

from .config import Config
from .objs.User import User

# convert host and list of participants to a list of users.
# host is int, participants list is list of strings: ["<@[id1]>", "<@[id2]>", ...]
def participants_to_users(bot: bot, host_id: int, participants_lst: list[str]): 
    user_lst = []

    disc_usr = bot.get_user(host_id)
    host_u = User(host_id, disc_usr, User.STATUS_HOST)
    user_lst.append(host_u)
    # turn participants into User objects and append them to user list
    for p_str in participants_lst:
        # NOTE: this results in the id being extracted from the string only to be added back inside of the User constructor.
        # bad efficiency but done for the sake for readability
        match = re.search(r"<@(\d+)>", p_str)
        id = int(match.group(1))
        disc_usr = bot.get_user(id)

        u = User(id, disc_usr, User.STATUS_UNDECIDED)
        user_lst.append(u)
    
    return user_lst

def to_datetime(time: str, input_day: int, input_month: int, input_year: int, timezone: zoneinfo.ZoneInfo):
    now = datetime.datetime.now().astimezone() # astimezone() defaults to the local timezone

    day = input_day if input_day else now.day
    month = input_month if input_month else now.month
    year = input_year if input_year else now.year
    
    # regex magic to extract the 1 (+2 optional) components from time string (11:59pm -> pulls out 11, 59, pm)
    # if minutes is missing, 0 is assumed. if period is missing, 24 hour format is assumed
    match = re.match(r"^(\d{1,2})(?::(\d{2}))?\s?([apAP][mM])?$", time)
    hr = int(match.group(1))
    min = int(match.group(2)) if match.group(2) else 0
    period = match.group(3).lower() if match.group(3) else None

    # convert 12 hour to 24 hour time
    # period will be discarded if a 24hr time is inputted with period (eg. 15:00am will be taken as 15:00 = 3:00pm)
    if (hr < 12 and period == "pm"):
        hr += 12
    elif hr == 12 and period == "am":
        hr = 0

    event_datetime = datetime.datetime(year, month, day, hr, min, tzinfo=timezone)

    print(event_datetime)
    # enforce a future time (ie. if they choose 3:00pm and its 11:59pm, then set day as tomorrow rather than taking today)
    if event_datetime < now:
        if not input_day:
            event_datetime += relativedelta.relativedelta(days=1)
        elif input_day and not input_month:
            event_datetime += relativedelta.relativedelta(months=1)
        elif input_day and input_month and not input_year:
            event_datetime += relativedelta.relativedelta(years=1)

    return event_datetime

# update active dict with new/changed timezone and write the new dictionary to JSON
# TODO: this should maybe only write to json on close instead of on every update
def update_timezone(user_timezones: dict, id: int, timezone: str):
    user_timezones[str(id)] = timezone

def read_timezone_json():
    with open(Config.TIMEZONE_JSON_DIR, "r") as f:
        try:
            user_timezones = json.load(f)
            return user_timezones
        except:
            return {}

def write_timezone_json(user_timezones: dict):
    # opening the file with type 'w' causes writes (dump) to overwrite the entire file
    with open(Config.TIMEZONE_JSON_DIR, "w") as f:
        json.dump(user_timezones, f)