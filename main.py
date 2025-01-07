import discord
import time
from discord import ui, Button, Embed
from datetime import date
import json
import threading
import firebase_admin
from firebase_admin import credentials,firestore

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
staffRoles = [1076075894722023435]

@bot.slash_command(guild_ids=servers,name='latency',description='To get the bots response time.')
async def latency(ctx):
    await ctx.respond(f"**Latency :** `{int(bot.latency*1000)}ms`")








































































































































































bot.run(readJson('./config.json','TOKEN'))    