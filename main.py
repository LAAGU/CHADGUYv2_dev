import discord
import time
from discord import ui, Button, Embed, Option
from discord.ext import commands
from typing import Annotated
from datetime import date
import json
import threading
import firebase_admin
from firebase_admin import credentials,firestore
from functions import *
import random
from functools import wraps
import asyncio
import os,sys
import colorama
from colorama import Fore
colorama.init(autoreset=True)

try:

  def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

  encryption_map, decryption_map = create_mapping()
  
  cred = credentials.Certificate(resource_path("cbv2pk.json"))
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
  
  def addMoney(userID: int, amount: int | float, type: str = "bank"):
      if type == "wallet":
          db.collection("accounts").document(str(userID)).update({"money.wallet": firestore.Increment(amount)})
      else:
          db.collection("accounts").document(str(userID)).update({"money.bank": firestore.Increment(amount)})
  
  def removeMoney(userID: int, amount: int | float, type: str = "bank"):
      if type == "wallet":
          db.collection("accounts").document(str(userID)).update({"money.wallet": firestore.Increment(-amount)})
      else:
          db.collection("accounts").document(str(userID)).update({"money.bank": firestore.Increment(-amount)})
  
  
  servers = [1055476996077015141]
  staffRole = 1076075894722023435
  earlyAccessRole = 1097927212784693298
  commandLogsChannel = 1325869256486686782
  xmarkEmoji = "<:xmark:1326705481854619680>"
  tickEmoji = "<:tick:1326705494198321294>"
  
  
  intents = discord.Intents.all()
  
  bot = discord.Bot(intents=intents)
  version = "2.0.0"

  @bot.event
  async def on_ready():
      text = f"{bot.user.name} Started\nID: {bot.user.id}\nVersion: {version}"
      print(Fore.LIGHTGREEN_EX + text)
      print(Fore.CYAN + "Also Join Our Discord At: https://discord.gg/ZxaDHm6jc4")
  
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
  
  messageTimeout = {}
  TimeoutCount = {}
  
  def MessageSpamProtection(timeout):
      def decorator(func):
          @wraps(func)
          async def wrapper(message, *args, **kwargs):
              current_time = time.time()
              user_id = message.author.id
  
              if message.author.bot:
                  return await func(message, *args, **kwargs)
  
              if user_id in messageTimeout:
                  time_left = messageTimeout[user_id] - current_time
                  embed = discord.Embed(
                          title="<:csp:1326700853930754080> Slow Down !",
                          description=f"### You are Going Too Fast!",
                          color=discord.Color.red()
                      )
                  embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1128242859078852648/1326701102237880330/csp_logo.png?ex=6780622f&is=677f10af&hm=c49f053ef0bb3ce7b8a14f7ce540dfd02d5650a534a6efa02c9c782c5b3a78ad&")
                  embed.set_footer(
                          text="Spam Protection By sukrit_thakur",
                          icon_url="https://cdn.discordapp.com/avatars/774179600800284682/f90d1b3530e364ec8572ce92463c6c00.png?size=1024"
                      )
                  if time_left > 0:
                      await message.delete()
                      if TimeoutCount[user_id] < 1:
                          TimeoutCount[user_id] += 1
                      else:
                          TimeoutCount[user_id] += 1   
                          msg = await message.channel.send(embed=embed)
                          await msg.delete(delay=2)
                      return
  
              await func(message, *args, **kwargs)
              TimeoutCount[user_id] = 0
              messageTimeout[user_id] = current_time + timeout
              threading.Timer(timeout, lambda: messageTimeout.pop(user_id, None)).start()
  
          return wrapper
      return decorator
  
  
  @bot.event
  @MessageSpamProtection(1)
  async def on_message(message):
      if message.author.bot:
          return    
  
  @bot.event
  async def on_application_command_error(ctx,error):
      if isinstance(error,commands.CommandOnCooldown):
          await ctx.respond(f"- **{error}** {xmarkEmoji}",ephemeral=True,delete_after=2)
      else:
          raise error    
  
  
  def hasAccount():
      def decorator(func):
          @wraps(func)
          async def wrapper(ctx, *args, **kwargs):
              hasAcc = rdb("accounts",str(ctx.author.id))
              if hasAcc != None:
                  return await func(ctx, *args, **kwargs)
              else:
                  await ctx.respond(f"- **You do not have an account to use this command {xmarkEmoji}, use the command `/register` to create one.**", ephemeral=True)
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
                  await ctx.respond(f"- **You do not have __Early Access Role__ to use this command {xmarkEmoji}**", ephemeral=True)
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
                  await ctx.respond(f"- **You do not have the required permissions to use this command {xmarkEmoji}**", ephemeral=True)
                  return
          return wrapper
      return decorator
  
  commandRateLimit = 1
  commandCoolDown = 5
  
  
  @bot.slash_command(guild_ids=servers,name='latency',description='To get the bots response time.')
  @commands.cooldown(commandRateLimit,commandCoolDown,commands.BucketType.user)
  @isBetaUser()
  async def latency(ctx):
      await ctx.respond(f"**Latency :** `{int(bot.latency*1000)}ms`")
  
  @bot.slash_command(guild_ids=servers,name='agent',description='Get a random agent.')
  @commands.cooldown(commandRateLimit,commandCoolDown * 2,commands.BucketType.user)
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
  @commands.cooldown(commandRateLimit,commandCoolDown,commands.BucketType.user)
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
  @commands.cooldown(commandRateLimit,commandCoolDown,commands.BucketType.user)
  @isStaff()
  @isBetaUser()
  async def clear(ctx,amount=1):
      await ctx.defer(ephemeral=True)
      if int(amount) > 100:
          await ctx.respond(f"- **You can't clear more than 100 messages {xmarkEmoji}**",ephemeral=True)
          return
      await ctx.channel.purge(limit=int(amount))
      await ctx.respond(f"- **Cleared `{amount}` message(s) {tickEmoji}**",ephemeral=True)
      
  
  @bot.slash_command(guild_ids=servers, name='register', description='Create an account.')
  @commands.cooldown(commandRateLimit,commandCoolDown * 3,commands.BucketType.user)
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
       return await ctx.respond(f"- **You already have an account {xmarkEmoji}**",ephemeral=True)
      cdb("accounts",data,str(ctx.author.id))
      await ctx.respond(f"- **Account created successfully {tickEmoji}**",ephemeral=True)
  
  
  @bot.slash_command(guild_ids=servers, name='balance', description='Check your balance.')
  @commands.cooldown(commandRateLimit,commandCoolDown * 2,commands.BucketType.user)
  @isBetaUser()
  @hasAccount()
  async def balance(ctx,hidden: str = "true"):
      await ctx.defer(ephemeral=hidden.lower() not in ["false", "no"])
      data = rdb("accounts",str(ctx.author.id))
      embed = discord.Embed(title=f"Your Balance {ctx.author.display_name}", description=f"## <:_bank:1326706646977875988>Bank : `${'{:,}'.format(data['money']['bank'])}`\n### <:_wallet:1326706644591312906> Wallet : `${'{:,}'.format(data['money']['wallet'])}`", color=discord.Color.green())
      await ctx.respond(embed=embed,ephemeral=hidden=="True")
  
  
  
  robbed = []
  
  @bot.slash_command(guild_ids=servers, name='rob', description='Rob Someone.')
  @commands.cooldown(commandRateLimit,commandCoolDown * 4,commands.BucketType.user)
  @isBetaUser()
  @hasAccount()
  async def rob(ctx : discord.ApplicationContext,user: Annotated[discord.Member, Option(discord.Member,"Select whose wallet you want to rob")]):
      await ctx.defer(ephemeral=True)
  
      if ctx.author.id == user.id:
          return await ctx.respond(f"- **You cannot rob yourself {xmarkEmoji}**")
  
      for rob in robbed:
          if rob["robber"] == ctx.author.id:
              return await ctx.respond(f"- **You just robbed someone wait sometime before you can rob again {xmarkEmoji}**")
  
      if user.status.value in ['dnd','offline']:
          return await ctx.respond(f"- **{user.display_name} is currently in `{user.status.value.upper()}` Mode, So you cannot rob them {xmarkEmoji}**")
      if not rdb("accounts",str(user.id)):    
         return await ctx.respond(f"- **{user.display_name} Does not have a wallet {xmarkEmoji}**")
      cashOnPerson = rdb("accounts",str(user.id))["money"]["wallet"]
  
      cashFound = 0
      if (cashOnPerson <= 0):
          return await ctx.respond(f"- **There was no money in {user.display_name}'s wallet {xmarkEmoji}**")
      if (cashOnPerson < 500):
          cashFound = random.randint(1,cashOnPerson)
      else:
          cashFound = random.randint(5,500)
      try:
          removeMoney(str(user.id),cashFound,"wallet")
          addMoney(str(ctx.author.id),cashFound,"wallet")
          robbedData = {
              "robber": ctx.author.id,
              "robbed": user.id,
              "amount": cashFound
          }
          robbed.append(robbedData)
          threading.Timer(120, lambda: robbed.remove(robbedData).start())
          await ctx.respond(f"- **You successfully robbed `${'{:,}'.format(cashFound)}` {tickEmoji}**")
          await ctx.channel.send(f"**{user.mention}, Your wallet was just robbed of `${'{:,}'.format(cashFound)}`, You have 2min to find who it was with the command `/findrobber [name]`**")
  
      except Exception as e:
          await ctx.respond(f"- **There was an error :** `{e}`")
  
     
  @bot.slash_command(guild_ids=servers, name='findrobber', description='Find the person who robbed you.')
  @commands.cooldown(commandRateLimit,commandCoolDown,commands.BucketType.user)
  @isBetaUser()
  @hasAccount()
  async def findrobber(ctx : discord.ApplicationContext,user: Annotated[discord.Member, Option(discord.Member,"Select the person who you think robbed you.")]):
      await ctx.defer()
  
      if ctx.author.id == user.id:
          return await ctx.respond(f"- {xmarkEmoji} **You cannot find yourself**")
  
      robbedData: dict = {
          "robbed": None
      }
      for data in robbed:
          if data["robbed"] == ctx.author.id:
              robbedData = data
              break
      if data["robbed"] == user.id:
          return await ctx.respond(f"- {xmarkEmoji} **{user.display_name} was robbed he is not the robber**")
      
      if robbedData["robbed"] == None:
          return await ctx.respond(f"- {xmarkEmoji} **There is no sus person here, Better Luck Next Time**")
      if robbedData["robber"] != user.id:
          return await ctx.respond(f"- {xmarkEmoji} **The person who robbed you is not {user.display_name}**")              
      await ctx.respond(f"- {tickEmoji} **You found the person!,It was {user.mention}**")
      try:
       robbed.remove(robbedData) 
       await ctx.followup.send(f"- **You got your `${'{:,}'.format(robbedData['amount'])}` Back!**")   
       userMoney = rdb("accounts",str(user.id))["money"]
       if userMoney["wallet"] - robbedData['amount'] <= 0:
           costing = random.randint(1,20)
           if userMoney["bank"] >= 20:
              removeMoney(str(user.id),robbedData['amount'] + costing,"bank")
              addMoney(str(ctx.author.id),robbedData['amount'] + costing,"wallet")
              return await ctx.followup.send(f"- **You also beat {user.display_name} and took all of their belongings costing `${'{:,}'.format(costing)}`**")
           else:
              return await ctx.followup.send(f"- **You also beat {user.display_name} but they did not have any money on them**")
       if userMoney["wallet"] - robbedData['amount'] > 5:
           costing = random.randint(1,5)
           removeMoney(str(user.id),robbedData['amount'] + costing,"wallet")
           addMoney(str(ctx.author.id),robbedData['amount'] + costing,"wallet")
           return await ctx.followup.send(f"- **You also beat {user.display_name} and took all of their belongings costing `${'{:,}'.format(costing)}`**")
       if userMoney["wallet"] - robbedData['amount'] > 500:
           costing = random.randint(50,500)
           removeMoney(str(user.id),robbedData['amount'] + costing,"wallet")
           addMoney(str(ctx.author.id),robbedData['amount'] + costing,"wallet")
           return await ctx.followup.send(f"- **You also beat {user.display_name} and took all of their belongings costing `${'{:,}'.format(costing)}`**")
      except Exception as e:
          await ctx.followup.send(f"- **There was an error :** `{e}`")
  
  
  @bot.slash_command(guild_ids=servers, name='deposit', description='Deposit your wallet money to bank.')
  @commands.cooldown(commandRateLimit,commandCoolDown * 2,commands.BucketType.user)
  @isBetaUser()
  @hasAccount()
  async def deposit(ctx : discord.ApplicationContext,amount: str):
      await ctx.defer(ephemeral=True)
  
      try:
          amount = int(amount)
      except ValueError:
          return await ctx.respond(f"- **Invalid input: Please enter a valid number {xmarkEmoji}**")
  
      if int(amount) > rdb("accounts",str(ctx.author.id))["money"]["wallet"]:
          return await ctx.respond(f"- **You cannot deposit more than your wallet balance {xmarkEmoji}**")
  
      removeMoney(str(ctx.author.id),int(amount),"wallet")
      addMoney(str(ctx.author.id),int(amount),"bank")
      await ctx.respond(f"- **You successfully deposited `${'{:,}'.format(int(amount))}` {tickEmoji}**")
  
  @bot.slash_command(guild_ids=servers, name='withdraw', description='Withdraw your bank money to wallet.')
  @commands.cooldown(commandRateLimit,commandCoolDown * 2,commands.BucketType.user)
  @isBetaUser()
  @hasAccount()
  async def withdraw(ctx : discord.ApplicationContext,amount: str):
      await ctx.defer(ephemeral=True)
  
      try:
          amount = int(amount)
      except ValueError:
          return await ctx.respond(f"- **Invalid input: Please enter a valid number {xmarkEmoji}**")
  
      if int(amount) > rdb("accounts",str(ctx.author.id))["money"]["bank"]:
          return await ctx.respond(f"- **You cannot withdraw more than your bank balance {xmarkEmoji}**")
  
      removeMoney(str(ctx.author.id),int(amount),"bank")
      addMoney(str(ctx.author.id),int(amount),"wallet")
      await ctx.respond(f"- **You successfully withdrew `${'{:,}'.format(int(amount))}` {tickEmoji}**")
  
  @bot.slash_command(guild_ids=servers, name='depall', description='Deposit all your money to bank.')
  @commands.cooldown(commandRateLimit,commandCoolDown * 5,commands.BucketType.user)
  @isBetaUser()
  @hasAccount()
  async def depall(ctx : discord.ApplicationContext):
      await ctx.defer(ephemeral=True)
      walletamount = rdb("accounts",str(ctx.author.id))["money"]["wallet"]
  
      if walletamount <= 0:
          return await ctx.respond(f"- **You do not have any money to deposit {xmarkEmoji}**")
  
      removeMoney(str(ctx.author.id),walletamount,"wallet")
      addMoney(str(ctx.author.id),walletamount,"bank")
      await ctx.respond(f"- **You successfully deposited all your money {tickEmoji}**")
  
  
  settings = rdb('about-bot','settings')
  
  if settings == None:
      raise ConnectionError(Fore.RED + "Can't fetch settings")
  elif settings["version"] != version:
      raise ConnectionRefusedError(Fore.RED + f"Version Mismatch:" + Fore.YELLOW + f"\nCurrent: {version}" + Fore.GREEN + f"\nRequired: {settings['version']}")
  elif settings["maintenance"] == True:
      raise PermissionError(Fore.LIGHTYELLOW_EX + "Bot is currently under maintenance")
  else:
      bot.run(decrypt_string(settings["TOKEN"],decryption_map))  
  pass
except Exception as e:
    print(Fore.RED + f"An error occurred: {e}")
    input(Fore.RED + "Press Enter to exit...")  