import discord
from discord.ext import commands
from json import loads
from random import randrange
import os.path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from activities import ACTIVITY_INFO
from flashbot_secrets import DISCORD_SECRET
#from requests_oauthlib import OAuth2Session

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

DEFAULT_SESSION_TIME_MINUTES = 60

ACTIVITY_TYPE_EITHER = 0
ACTIVITY_TYPE_OPENER = 1
ACTIVITY_TYPE_MAIN = 2

SCOPES = ['https://www.googleapis.com/auth/presentations']

@client.group()
async def create(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Known activities are: [" + ' | '.join(list(ACTIVITY_INFO.keys())) + "]")

@create.command()
async def stoplight(ctx, *, message: str=""):
    if message != "":
        creds = None
        
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            terms = message.split(",")

            if len(terms) > 6:
                await ctx.send(ACTIVITY_INFO['stoplight']['syntax'])
                return

            await ACTIVITY_INFO['stoplight']['function'](ctx, creds, terms=terms)
        except HttpError as error:
            await ctx.send(f'An error occurred: {error}')
    else:
        await ctx.send(ACTIVITY_INFO['stoplight']['syntax'])

@create.command()
async def catastrophe(ctx, *, message: str=""):
    if message != "":
        info = message.split(",", 1)

        if len(info) == 2:
            mural_name = info[0]
            info[1] = info[1].strip()
            terms = info[1].split(',')

            await ACTIVITY_INFO['catastrophe']['function'](ctx, mural_name, terms)
        else:
            await ctx.send(ACTIVITY_INFO['catastrophe']['syntax'])
    else:
        await ctx.send(ACTIVITY_INFO['catastrophe']['syntax'])

@create.command()
async def answer_quest(ctx, *, message: str=""):
    if message != "":
        info = message.split(",", 1)

        if len(info) == 2:
            mural_name = info[0]
            info[1] = info[1].strip()

            split_list = info[1].split('|')

            if len(split_list) == 2:
                terms = {}
                terms['terms'] = split_list[0].split(',')
                terms['definitions'] = split_list[1].split(',')

                await ACTIVITY_INFO['answer_quest']['function'](ctx, mural_name, terms)
            else:
                await ctx.send(ACTIVITY_INFO['answer_quest']['syntax'])
        else:
            await ctx.send(ACTIVITY_INFO['answer_quest']['syntax'])
    else:
        await ctx.send(ACTIVITY_INFO['answer_quest']['syntax'])

@create.command()
async def mural(ctx, *, message: str=""):
    if message != "":
        await ACTIVITY_INFO['mural']['function'](ctx, message)
    else:
        await ctx.send(ACTIVITY_INFO['mural']['syntax'])

@client.command()
async def sessionplan(ctx, *args):
    num_args = len(args)

    if num_args == 0:
        await create_plan(ctx)
    elif num_args >= 1:
        props = {'virtual': False, 'lowprep': False}

        for name in props.keys():
            if name in args:
                props[name] = True
        
        await create_plan(ctx, virtual=props['virtual'], lowprep=props['lowprep'])

@client.command()
async def activity(ctx, *args):
    if len(args) > 0:
        name = (' '.join(args)).lower()

        for i in range(num_strategies):
            if strategies[i]['name'].lower() == name:
                await ctx.send(strategies[i]['name'] + ' description: ' + strategies[i]['description'] + '\nVARK: ' + strategies[i]['vark'])
                return
        
        await ctx.send(name + ' not found!')
    else:
        await ctx.send('Please include the name of an activity')

@client.command()
async def schedule(ctx, *, message: str = ""):
    if message != "":
        campus = message.lower()
        campus_codes = {"northeast": "NE", "ne": "NE", "northwest": "NW", "nw": "NW", "south": "South", "so": "South", "southeast": "SE", "se": "SE", "trinity": "TR", "trinity river": "TR", "tr": "TR", "connect": "CN", "cn": "CN"}
        
        if campus in campus_codes.keys():
            await ctx.send("TCC " + campus_codes[campus] + " SI schedule: <https://tinyurl.com/TCC" + campus_codes[campus] + "SISchedule>")
        else:
            await ctx.send("Campus '" + campus + "' not found. Perhaps you have a typo?")
    else:
        await ctx.send("Please include a campus name or abbreviation")

@client.command()
async def helpdocs(ctx, *args):
    await ctx.send("See Flashbot's help documentation here: <https://github.com/Geforce132/Flashbot/blob/main/README.md>")

async def create_plan(ctx, minutes=DEFAULT_SESSION_TIME_MINUTES, virtual=False, lowprep=False):
    good_plan = False
    
    while not good_plan:
        activity_types = [ACTIVITY_TYPE_OPENER, ACTIVITY_TYPE_MAIN, ACTIVITY_TYPE_MAIN, ACTIVITY_TYPE_EITHER, ACTIVITY_TYPE_OPENER]
        times = pick_time_layout(minutes)
        sel_strats = []
        vark = ''

        for i in range(5):
            strat = pick_activity(sel_strategies=sel_strats, activity_type=activity_types[i], virtual=virtual, lowprep=lowprep)
            vark += strat['vark']
            sel_strats.append(strat)
        
        if check_plan(sel_strats, vark, times):
            good_plan = True
    
    props = ''
    if virtual:
        props += '🖥️ '

    if lowprep:
        props += '😴 '

    embed = discord.Embed(title="Here's a session plan for you!\nType: " + (props.strip() if props else 'normal'))

    activity_names = ['Opener', 'Main activity 1', 'Main activity 2', 'Backpocket activity', 'Closer']
    for index, strat in enumerate(sel_strats):
        embed.add_field(name=activity_names[index], value=f"{strat['name']} {' '.join(get_activity_emoji_string(strat))}\nTime: {times[index]} - VARK: {strat['vark']}", inline=False)

    await ctx.send(embed=embed)

def check_plan(strategies, vark, times):
    good_plan = False

    has_all_vark = 'V' in vark and 'A' in vark and 'R' in vark and 'K' in vark
    if has_all_vark:
        vark_times = dict(V=0, A=0, R=0, K=0)

        for i, strat in enumerate(strategies):
            time_to_add = times[i] if times[i] != 'filler' else 0
            
            if 'V' in strat['vark']:
                vark_times['V'] += time_to_add

            if 'A' in strat['vark']:
                vark_times['A'] += time_to_add

            if 'R' in strat['vark']:
                vark_times['R'] += time_to_add

            if 'K' in strat['vark']:
                vark_times['K'] += time_to_add
        
        if all(value > 15 for value in vark_times.values()):
            good_plan = True

    return good_plan

def pick_activity(sel_strategies=[], activity_type=ACTIVITY_TYPE_MAIN, virtual=False, lowprep=False):
    good_act = False
    iterations = 0

    while not good_act:
        iterations += 1
        act = strategies[randrange(1, num_strategies)]

        # already selected
        if act in sel_strategies:
            continue

        # not the correct type of activity
        if not ACTIVITY_TYPE_EITHER:
            if (act['main_activity'] == 'true' and activity_type == ACTIVITY_TYPE_OPENER) or (act['main_activity'] == 'false' and activity_type == ACTIVITY_TYPE_MAIN):
                continue

        # not a virtual activity if needed
        if virtual and not act['virtual'] == 'true':
            continue

        # not a lowprep activity if needed
        if lowprep and not act['low_prep'] == 'true':
            continue

        # same VARK designations as the previous activity
        if len(sel_strategies) >= 1 and sel_strategies[-1]['vark'] == act['vark']:
            continue

        # too much of this VARK type of activity already selected
        if iterations <= 100:
            excessive_vark = False
            counts = get_strategy_vark_counts(sel_strategies)
            for char in 'VARK':
                if counts[char] >= 3 and char in act['vark']:
                    excessive_vark = True
        
            if excessive_vark:
                continue

        good_act = True

    return act

def get_activity_emoji_string(activity):
    vark = activity['vark']
    str = ''

    if 'V' in vark:
        str += '👀'
    
    if 'A' in vark:
        str += '🗣️'
    
    if 'R' in vark:
        str += '📝'

    if 'K' in vark:
        str += '🏃'

    return str

def get_strategy_vark_counts(strats):
    counts = dict(V=0, A=0, R=0, K=0)

    for i in strats:
        if 'V' in i['vark']:
            counts['V'] += 1
    
        if 'A' in i['vark']:
            counts['A'] += 1
    
        if 'R' in i['vark']:
            counts['R'] += 1

        if 'K' in i['vark']:
            counts['K'] += 1
    
    return counts

def pick_time_layout(minutes=DEFAULT_SESSION_TIME_MINUTES):
    times = [
        [10, 20, 20, "filler", 10],
        [10, 20, 20, "filler", 10],
        [10, 20, 20, "filler", 10],
        [10, 20, 20, "filler", 10],
        [10, 15, 25, "filler", 10],
        [15, 20, 20, "filler", 5]
    ]

    short_times = [
        [10, 15, 20, "filler", 5],
        [10, 15, 20, "filler", 5],
        [10, 15, 20, "filler", 5],
        [5, 20, 20, "filler", 5],
        [10, 15, 15, "filler", 10]
    ]

    if minutes == 50:
        return short_times[randrange(0, len(short_times))]
    else:
        return times[randrange(0, len(times))]

if __name__ == "__main__":
    with open('cards.json', 'r', encoding='utf-8') as file:
        strategies = loads(file.read())['strategies']
        num_strategies = len(strategies)

    # Last line
    client.run(DISCORD_SECRET)


