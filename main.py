import discord
import time
from discord import ui, Button, Embed, Option
from datetime import date
import json
import threading
import firebase_admin
from firebase_admin import credentials,firestore
from functions import *
import random
from functools import wraps
import asyncio
encryption_map, decryption_map = create_mapping()


cred = credentials.Certificate("./cbv2pk.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# [Read from Database]
def rdb(collection : str,document_id : str):
    doc_ref = db.collection(collection).document(document_id).get()
    if doc_ref.exists:
       return doc_ref.to_dict()
    else:
       return None

# [Create in Database]
def cdb(collection_name : str,data : dict,custom_id : str = None):
   if not custom_id:
    db.collection(collection_name).add(data)
   else:
    db.collection(collection_name).document(custom_id).set(data) 

# [Delete from DataBase]
def ddb(collection_name : str,document_id : str):
    db.collection(collection_name).document(document_id).delete()

# [Update in Database]
def udb(collection_name : str,document_id : str,data : dict):
    db.collection(collection_name).document(document_id).update(data)


def readJson(filePath : str,key : str) -> dict:
    try: 
     with open(filePath) as f:
      data = json.load(f)
      return data[key]
    except Exception as e:
        print(e) 
    
def writeJson(filePath : str,key : str,value : any):
    try:   
     with open(filePath) as f:
        data = json.load(f)
        data[key] = value
        with open(filePath,'w') as f:
            json.dump(data,f,indent=4)
    except Exception as e:
        print(e)           

def addMoney(userID : int,amount : int | float,type : str = "bank"):
   if type == "wallet":
      db.collection("accounts").document(str(userID)).update({"money":{"wallet": firestore.Increment(amount)}})
   else:
      db.collection("accounts").document(str(userID)).update({"money":{"bank": firestore.Increment(amount)}})

def removeMoney(userID : int,amount : int | float,type : str = "bank"):
   if type == "wallet":
      db.collection("accounts").document(str(userID)).update({"money":{"wallet": firestore.Increment(-amount)}})
   else:
      db.collection("accounts").document(str(userID)).update({"money":{"bank": firestore.Increment(-amount)}})


servers = [1055476996077015141]
staffRole = 1076075894722023435
earlyAccessRole = 1097927212784693298
commandLogsChannel = 1325869256486686782

commandTimeout = {}

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f'BOT is running as {bot.user}')

@bot.event
async def on_application_command(ctx: discord.ApplicationContext):
    user = ctx.author
    command_name = ctx.command.name
    command_id = ctx.command.id
    options = ctx.interaction.data.get('options', [])
    args = [option['value'] for option in options]
    embed = discord.Embed(title="Command Executed By An User",description=f"```fix\nName: {user.name}\nID: {user.id}\nCommandName: {command_name}\nCommandID: {command_id}\nArguments: {str(','.join(args))}\nTime: {time.strftime('%d-%m-%Y %H:%M:%S', time.localtime())}\n```", color=discord.Color.blue())
    channel = bot.get_channel(commandLogsChannel)
    await channel.send(embed=embed)



def CommandSpamProtection(timeout=5):
    def decorator(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            current_time = time.time()
            user_id = ctx.author.id

            if user_id in commandTimeout:
                time_left = commandTimeout[user_id] - current_time
                if time_left > 0:
                    embed = discord.Embed(title="<:csp:1326700853930754080> You are on cooldown !",description=f"### Time Left :\n- **{int(time_left)}s**",color=discord.Color.red())
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1128242859078852648/1326701102237880330/csp_logo.png?ex=6780622f&is=677f10af&hm=c49f053ef0bb3ce7b8a14f7ce540dfd02d5650a534a6efa02c9c782c5b3a78ad&")
                    embed.set_footer(text="Command Spam Protection By sukrit_thakur",icon_url="https://cdn.discordapp.com/avatars/774179600800284682/f90d1b3530e364ec8572ce92463c6c00.png?size=1024")
                    await ctx.respond(embed=embed, ephemeral=True)
                    commandTimeout[user_id] = current_time + timeout
                    return

            await func(ctx, *args, **kwargs)

            commandTimeout[user_id] = current_time + timeout
            threading.Timer(timeout, lambda: commandTimeout.pop(user_id, None)).start()

        return wrapper
    return decorator

def hasAccount():
    def decorator(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            hasAcc = rdb("accounts",str(ctx.author.id))
            if hasAcc != None:
                return await func(ctx, *args, **kwargs)
            else:
                await ctx.respond("- **You do not have an account to use this command <:xmark:1326705481854619680>, use the command `/register` to create one.**", ephemeral=True)
                return
        return wrapper
    return decorator


def isBetaUser():
    def decorator(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            if not isinstance(ctx.author, discord.Member):
                ctx.author = await ctx.guild.fetch_member(ctx.author.id)

            role = discord.utils.get(ctx.author.roles, id=earlyAccessRole)
            if role:
                return await func(ctx, *args, **kwargs)
            else:
                await ctx.respond("- **You do not have __Early Access Role__ to use this command <:xmark:1326705481854619680>**", ephemeral=True)
                return
        return wrapper
    return decorator

def isStaff():
    def decorator(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            if not isinstance(ctx.author, discord.Member):
                ctx.author = await ctx.guild.fetch_member(ctx.author.id)

            role = discord.utils.get(ctx.author.roles, id=staffRole)
            if role:
                return await func(ctx, *args, **kwargs)
            else:
                await ctx.respond("- **You do not have the required permissions to use this command <:xmark:1326705481854619680>**", ephemeral=True)
                return
        return wrapper
    return decorator




@bot.slash_command(guild_ids=servers,name='latency',description='To get the bots response time.')
@CommandSpamProtection()
@isBetaUser()
async def latency(ctx):
    await ctx.respond(f"**Latency :** `{int(bot.latency*1000)}ms`")

@bot.slash_command(guild_ids=servers,name='agent',description='Get a random agent.')
@CommandSpamProtection(10)
@isBetaUser()
async def agent(ctx):
   embed = discord.Embed(title="Your Agent Is -", description=f"## LOADING...\n- ...", color=discord.Color.yellow())
   embed.set_image(url="https://cdn.dribbble.com/users/756637/screenshots/2249870/slot-machine-main-2.gif")
   msg = await ctx.respond(embed=embed)
   await asyncio.sleep(1.5)
   agent = GetAgent(random.randint(0,27))
   embed.set_image(url=random.choice(agent['img']))
   embed.description = f"## {agent['name']}\n- {agent['info']}"
   await msg.edit(embed=embed)



@bot.slash_command(guild_ids=servers, name='test_agents', description='test random agent command.')
@CommandSpamProtection()
@isStaff()
@isBetaUser()
async def test_agents(ctx):
    list = GetAgentList()
    await ctx.respond("Sending all agents 1 by 1...")
    await asyncio.sleep(1)
    for agent in list:
        try:
            await ctx.send(f"UPCOMING - {agent['name']}")
            embed = discord.Embed(
                title="Your Agent Is -",
                description=f"## {agent['name']}\n- {agent['info']}",
                color=discord.Color.yellow(),
            )
            embed.set_image(url=random.choice(agent['img']))
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            await ctx.send(f"Error in Sending - {agent['name']}")
        await asyncio.sleep(1)
    await ctx.send("All agents sent.")

@bot.slash_command(guild_ids=servers, name='clear', description='Clears chat messages.')
@CommandSpamProtection()
@isStaff()
@isBetaUser()
async def clear(ctx,amount=1):
    await ctx.defer(ephemeral=True)
    if int(amount) > 100:
        await ctx.respond("- **You can't clear more than 100 messages <:xmark:1326705481854619680>**",ephemeral=True)
        return
    await ctx.channel.purge(limit=int(amount))
    await ctx.respond(f"- **Cleared `{amount}` message(s) <:tick:1326705494198321294>**",ephemeral=True)
    

@bot.slash_command(guild_ids=servers, name='register', description='Create an account.')
@CommandSpamProtection(15)
@isBetaUser()
async def register(ctx):
    data = {
       "name": ctx.author.name,
       "money": {"wallet":0,"bank":500},
       "createdOn": firestore.SERVER_TIMESTAMP,
       "inventory": [
          {
             "id": "phone",
             "name": "Phone",
             "emoji": "<:phone:1326689224749219982>",
             "amount": 1
          }
       ]
    }
    await ctx.defer(ephemeral=True)
    if (rdb("accounts",str(ctx.author.id)) != None):
     return await ctx.respond(f"- **You already have an account <:xmark:1326705481854619680>**",ephemeral=True)
    cdb("accounts",data,str(ctx.author.id))
    await ctx.respond(f"- **Account created successfully <:tick:1326705494198321294>**",ephemeral=True)


@bot.slash_command(guild_ids=servers, name='balance', description='Check your balance.')
@CommandSpamProtection(10)
@isBetaUser()
@hasAccount()
async def balance(ctx,hidden: str = "true"):
    await ctx.defer(ephemeral=hidden.lower() not in ["false", "no"])
    data = rdb("accounts",str(ctx.author.id))
    embed = discord.Embed(title=f"Your Balance {ctx.author.display_name}", description=f"## <:_bank:1326706646977875988>Bank : `{'{:,}'.format(data['money']['bank'])}`\n### <:_wallet:1326706644591312906> Wallet : `{'{:,}'.format(data['money']['wallet'])}`", color=discord.Color.green())
    await ctx.respond(embed=embed,ephemeral=hidden=="True")

bot.run(decrypt_string(rdb('about-bot','settings')["TOKEN"],decryption_map))    