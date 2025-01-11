import discord
import time
from discord import ui, Button, Embed, Option
from discord.ui import View
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
  
  def updateInventory(userID: int, itemID: str, amount: int):
    if itemID not in GetItems():
        return {"status": "error", "message": f"Item {itemID} does not exist."}
    

    doc_ref = db.collection("accounts").document(str(userID))
    doc = doc_ref.get()
    
    if not doc.exists:
        return {"status": "error", "message": f"doc {str(userID)} does not exist."}
    
    inventory = doc.to_dict().get("inventory", [])
    item_found = False


    updated_inventory = []
    for item in inventory:
        if item["id"] == itemID:
            item_found = True
            new_amount = item["amount"] + amount
            if new_amount > 0:
                updated_inventory.append({"id": itemID, "amount": new_amount})
        else:
            updated_inventory.append(item)

    if not item_found and amount > 0:
        updated_inventory.append({"id": itemID, "amount": amount})

    doc_ref.update({"inventory": updated_inventory})
    return {"status": "success", "message": f"inventory of user {userID} Modified, Item: {itemID}, Amount: {amount}."}

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
      args = [str(option['value']) for option in options]
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
          await ctx.respond(f"- **{xmarkEmoji} {error}**",ephemeral=True,delete_after=2)
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
                  await ctx.respond(f"- **{xmarkEmoji} You do not have an account to use this command, use the command `/register` to create one.**", ephemeral=True)
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
                  await ctx.respond(f"- **{xmarkEmoji} You do not have __Early Access Role__ to use this command.**", ephemeral=True)
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
                  await ctx.respond(f"- **{xmarkEmoji} You do not have the required permissions to use this command.**", ephemeral=True)
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
          await ctx.respond(f"- **{xmarkEmoji} You can't clear more than 100 messages.**",ephemeral=True)
          return
      await ctx.channel.purge(limit=int(amount))
      await ctx.respond(f"- **{tickEmoji} Cleared `{amount}` message(s)**",ephemeral=True)
      
  
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
               "amount": 1
            }
         ]
      }
      await ctx.defer(ephemeral=True)
      if (rdb("accounts",str(ctx.author.id)) != None):
       return await ctx.respond(f"- **{xmarkEmoji} You already have an account!**",ephemeral=True)
      cdb("accounts",data,str(ctx.author.id))
      await ctx.respond(f"- **{tickEmoji} Account created successfully!**",ephemeral=True)
  
  
  @bot.slash_command(guild_ids=servers, name='balance', description='Check your balance.')
  @commands.cooldown(commandRateLimit,commandCoolDown * 2,commands.BucketType.user)
  @isBetaUser()
  @hasAccount()
  async def balance(ctx,hidden: str = "true"):
      await ctx.defer(ephemeral=hidden.lower() not in ["false", "no"])
      data = rdb("accounts",str(ctx.author.id))
      embed = discord.Embed(title=f"Your Balance {ctx.author.display_name}", description=f"## <:_bank:1327722064307818496> : `${'{:,}'.format(data['money']['bank'])}`\n## <:_cash:1327722066660688012> : `${'{:,}'.format(data['money']['wallet'])}`\n- **Total :** `${'{:,}'.format(data['money']['wallet'] + data['money']['bank'])}`", color=discord.Color.green())
      await ctx.respond(embed=embed,ephemeral=hidden=="True")
  
  
  
  robbed = []
  
  @bot.slash_command(guild_ids=servers, name='rob', description='Rob Someone.')
  @commands.cooldown(commandRateLimit,commandCoolDown * 4,commands.BucketType.user)
  @isBetaUser()
  @hasAccount()
  async def rob(ctx : discord.ApplicationContext,user: Annotated[discord.Member, Option(discord.Member,"Select whose wallet you want to rob")]):
      await ctx.defer(ephemeral=True)
  
      if ctx.author.id == user.id:
          return await ctx.respond(f"- **{xmarkEmoji} You cannot rob yourself.**")

      for rob in robbed:
          if rob["robbed"] == user.id:
              return await ctx.respond(f"- **{xmarkEmoji} {user.display_name} just got robbed so they don't have anything valuable.**")

      for rob in robbed:
          if rob["robber"] == ctx.author.id:
              return await ctx.respond(f"- **{xmarkEmoji} You just robbed someone wait sometime before you can rob again.**")
  
      if user.status.value in ['dnd','offline']:
          return await ctx.respond(f"- **{xmarkEmoji} {user.display_name} is currently in `{user.status.value.upper()}` Mode, So you cannot rob them.**")
      if not rdb("accounts",str(user.id)):    
         return await ctx.respond(f"- **{xmarkEmoji} {user.display_name} Does not have a wallet.**")
      cashOnPerson = rdb("accounts",str(user.id))["money"]["wallet"]
  
      cashFound = 0
      if (cashOnPerson <= 0):
          return await ctx.respond(f"- **{xmarkEmoji} There was no money in {user.display_name}'s wallet.**")
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
          await ctx.respond(f"- **{tickEmoji} You successfully robbed `${'{:,}'.format(cashFound)}`**")
          await ctx.channel.send(f"**{user.mention}, Your wallet was just robbed of `${'{:,}'.format(cashFound)}`!, You have 2min to find who it was with the command `/findrobber [name]`**")
  
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
  async def deposit(ctx : discord.ApplicationContext,amount: int):
      await ctx.defer(ephemeral=True)
      if amount > rdb("accounts",str(ctx.author.id))["money"]["wallet"]:
          return await ctx.respond(f"- **{xmarkEmoji} You cannot deposit more than your wallet balance.**")
  
      removeMoney(str(ctx.author.id),amount,"wallet")
      addMoney(str(ctx.author.id),amount,"bank")
      await ctx.respond(f"- **{tickEmoji} You successfully deposited `${'{:,}'.format(amount)}`**")
  
  @bot.slash_command(guild_ids=servers, name='withdraw', description='Withdraw your bank money to wallet.')
  @commands.cooldown(commandRateLimit,commandCoolDown * 2,commands.BucketType.user)
  @isBetaUser()
  @hasAccount()
  async def withdraw(ctx : discord.ApplicationContext,amount: int):
      await ctx.defer(ephemeral=True)

  
      if amount > rdb("accounts",str(ctx.author.id))["money"]["bank"]:
          return await ctx.respond(f"- **{xmarkEmoji} You cannot withdraw more than your bank balance.**")
  
      removeMoney(str(ctx.author.id),amount,"bank")
      addMoney(str(ctx.author.id),amount,"wallet")
      await ctx.respond(f"- **{tickEmoji} You successfully withdrew `${'{:,}'.format(amount)}`**")
  
  @bot.slash_command(guild_ids=servers, name='depall', description='Deposit all your money to bank.')
  @commands.cooldown(commandRateLimit,commandCoolDown * 5,commands.BucketType.user)
  @isBetaUser()
  @hasAccount()
  async def depall(ctx : discord.ApplicationContext):
      await ctx.defer(ephemeral=True)
      walletamount = rdb("accounts",str(ctx.author.id))["money"]["wallet"]
  
      if walletamount <= 0:
          return await ctx.respond(f"- **{xmarkEmoji} You do not have any money to deposit.**")
  
      removeMoney(str(ctx.author.id),walletamount,"wallet")
      addMoney(str(ctx.author.id),walletamount,"bank")
      await ctx.respond(f"- **{tickEmoji} You successfully deposited all your money to your bank.**")




  @bot.slash_command(guild_ids=servers, name='inventory', description='Open your inventory.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 3, commands.BucketType.user)
  @isBetaUser()
  @hasAccount()
  async def inventory(ctx: discord.ApplicationContext, hidden: str = "true", page: int = 1):
      await ctx.defer(ephemeral=hidden.lower() not in ["false", "no"])
      data = rdb("accounts", str(ctx.author.id))
      
      items_per_page = 12
      inventory = data["inventory"]
      total_pages = max((len(inventory) + items_per_page - 1) // items_per_page, 1)
  
      page = max(1, min(page, total_pages)) - 1 
  
      def create_embed(current_page: int) -> discord.Embed:
          start = current_page * items_per_page
          end = start + items_per_page
          page_items = inventory[start:end]
  
          embed = discord.Embed(
              title=f"{ctx.author.display_name}'s Inventory - Page {current_page + 1}/{total_pages}",
              color=discord.Color.green()
          )
          if len(page_items) == 0:
              embed.description = "## - Empty"  

          for item in page_items:
              itemData = GetItem(item["id"])
              embed.add_field(
                  name=f"{itemData["emoji"]} {itemData["name"]}",
                  value=f"`x{item['amount']}`",
                  inline=True
              )
          return embed
  
      current_page = page
      embed = create_embed(current_page)
  
      class PaginationView(View):
          def __init__(self):
              super().__init__(timeout=60)
              self.update_buttons()
  
          @discord.ui.button(label="", emoji="<:leftarrow:1327716449510494339>", style=discord.ButtonStyle.secondary)
          async def previous_button(self, button: Button, interaction: discord.Interaction):
              if interaction.user.id != ctx.author.id:
                  return
              nonlocal current_page
              current_page = max(0, current_page - 1)
              embed = create_embed(current_page)
              self.update_buttons()
              await interaction.response.edit_message(embed=embed, view=self)
  
          @discord.ui.button(label="", emoji="<:rightarrow:1327716447467733043>", style=discord.ButtonStyle.secondary)
          async def next_button(self, button: Button, interaction: discord.Interaction):
              if interaction.user.id != ctx.author.id:
                  return
              nonlocal current_page
              current_page = min(total_pages - 1, current_page + 1)
              embed = create_embed(current_page)
              self.update_buttons()
              await interaction.response.edit_message(embed=embed, view=self)
  
          def update_buttons(self):
              self.previous_button.disabled = current_page <= 0
              self.next_button.disabled = current_page >= total_pages - 1
  
      view = PaginationView()
  
      await ctx.respond(embed=embed, view=view)


  async def autocomplete_example(ctx: discord.AutocompleteContext):
    options = list(GetItems().keys())
    return [option for option in options if ctx.value.lower() in option.lower()]  

  @bot.slash_command(guild_ids=servers, name='modify_inventory', description='Add or Remove items from a inventory.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 5, commands.BucketType.user)
  @isBetaUser()
  @isStaff()
  async def modify_inventory(ctx: discord.ApplicationContext,user: discord.User,item_id:Annotated[str,Option(str, "Choose an item", autocomplete=autocomplete_example)],modification:int):
      await ctx.defer(ephemeral=True)
      request = updateInventory(user.id,item_id,modification)
      if request["status"] == "error":
          return await ctx.respond(f"- {xmarkEmoji} **{request['message']}**")
      if request["status"] == "success":
          return await ctx.respond(f"- {tickEmoji} **{request['message']}**")






















  
  settings = rdb('about-bot','settings')
  
  if settings == None:
      raise ConnectionError(Fore.RED + "Can't fetch settings")
  elif settings["version"] != version:
      raise ConnectionRefusedError(Fore.RED + f"Version Mismatch:" + Fore.YELLOW + f"\nCurrent: {version}" + Fore.GREEN + f"\nRequired: {settings['version']}" + Fore.CYAN + f"\nDownload The Latest Version({settings['version']}) From: linknotfound.com")
  elif settings["maintenance"] == True:
      raise PermissionError(Fore.LIGHTYELLOW_EX + "Bot is currently under maintenance")
  else:
      bot.run(decrypt_string(settings["TOKEN"],decryption_map))  
  pass
except discord.errors.ClientException as e:
    print(Fore.RED + f"Bot is already running or invalid state: {e}")
except Exception as e:
    print(Fore.RED + f"An error occurred: {e}")
    input(Fore.RED + "Press Enter to exit...")
