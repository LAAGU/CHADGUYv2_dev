import discord
import time
from discord import ui, Button, Embed
from datetime import date
import json
import threading
import firebase_admin
from firebase_admin import credentials,firestore
from functions import *
import random
from functools import wraps
import asyncio



cred = credentials.Certificate("./cbv2pk.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# [Read from Database]
def rdb(collection : str,document_id : str):
    doc_ref = db.collection(collection).document(document_id).get()
    if doc_ref.exists:
       return doc_ref.to_dict()
    else:
       print("Document does not exist")

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





bot = discord.Bot()

@bot.event
async def on_ready():
    print(f'BOT is running as {bot.user}')

servers = [1055476996077015141]
staffRole = 1076075894722023435
earlyAccessRole = 1097927212784693298


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
                await ctx.respond("- **You do not have __Early Access Role__ to use this command.**", ephemeral=True)
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
                await ctx.respond("- **You do not have the required permissions to use this command.**", ephemeral=True)
                return
        return wrapper
    return decorator


@bot.slash_command(guild_ids=servers,name='latency',description='To get the bots response time.')
@isBetaUser()
async def latency(ctx):
    await ctx.respond(f"**Latency :** `{int(bot.latency*1000)}ms`")

@bot.slash_command(guild_ids=servers,name='agent',description='Get a random agent.')
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


































































































































































bot.run(readJson('./config.json','TOKEN'))    