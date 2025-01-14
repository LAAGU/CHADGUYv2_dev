import discord
import time
from discord import ui, Button, Embed, Option
from discord.ui import View
from discord.ext import commands
from typing import Annotated
import datetime
from datetime import date
from dateutil import parser
import json
import threading
import firebase_admin
from firebase_admin import credentials,firestore
from functions import *
import random
from functools import wraps
import asyncio
import os,sys,re
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
  

  def get_product_version(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    match = re.search(r"prodvers=\(\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\)", content)
    if match:
        product_version = ".".join(match.groups())
        return product_version
    else:
        raise ValueError("Product version not found in the file.")

  encryption_map, decryption_map = create_mapping()
  
  version = get_product_version(resource_path('version_info.txt'))
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
  StaffCommands = ['test_agents','modify_inventory','set_topic','clear','modify_money','check_inv']
  
  
  intents = discord.Intents.all()
  
  bot = discord.Bot(intents=intents)


  async def CreatePages(ctx,list: list,fieldName:str,fieldValue:str,isInLine:bool,forHelpCMD:bool,forInv:bool,page: int = 1,title: str="CreatePages func",color = discord.Color.blurple(),itemPerPage: int = 12,Button_style = discord.ButtonStyle.secondary):
    items_per_page = itemPerPage
    total_pages = max((len(list) + items_per_page - 1) // items_per_page, 1)

    page = max(1, min(page, total_pages)) - 1 

    def create_embed(current_page: int) -> discord.Embed:
        start = current_page * items_per_page
        end = start + items_per_page
        page_items = list[start:end]

        embed = discord.Embed(
            title=f"{title} - Page {current_page + 1}/{total_pages}",
            color=color
        )
        if len(page_items) == 0:
            embed.description = "## - Empty"  
        if forInv:
         for item in page_items:
          itemData = GetItem(item["id"])
          embed.add_field(
            name=f"{itemData["emoji"]} {itemData["name"]}",
            value=f"`x{item['amount']}`",
            inline=True
          )
        elif forHelpCMD:
         for item in page_items:
          embed.add_field(
            name=f"{"<:Staff_Command:1328509290654466188> " if item["staff"] else "<:User_Command:1328514019102818376> "} </{item[fieldName]}:{item['id']}>",
            value=f"- `{item[fieldValue]}`",
            inline=isInLine
          )  
        else:
         for item in page_items:
          embed.add_field(
            name=f"{item[fieldName]}",
            value=f"`x{item[fieldValue]}`",
            inline=isInLine
          )   
        return embed

    current_page = page
    embed = create_embed(current_page)

    class PaginationView(View):
        def __init__(self):
            super().__init__(timeout=60)
            self.update_buttons()

        @discord.ui.button(label="", emoji="<:leftarrow:1327716449510494339>", style=Button_style)
        async def previous_button(self, button: Button, interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return
            nonlocal current_page
            current_page = max(0, current_page - 1)
            embed = create_embed(current_page)
            self.update_buttons()
            await interaction.response.edit_message(embed=embed, view=self)

        @discord.ui.button(label="", emoji="<:rightarrow:1327716447467733043>", style=Button_style)
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
  

  @bot.event
  async def on_ready():
      text = f"{bot.user.name} Started\nID: {bot.user.id}\nVersion: {str(version).removesuffix('.0')}"
      print(Fore.LIGHTGREEN_EX + text)
      print(Fore.CYAN + "Also Join Our Discord At: https://discord.gg/ZxaDHm6jc4")
  

  commandSpamWarnings = {}  
  commandTimeouts = {}

  @bot.event
  async def on_application_command(ctx: discord.ApplicationContext):
      botSpamLogChannel = bot.get_channel(1327836541589917836)

      if ctx.command.name == "collect" and ctx.channel_id != 1327823326814670888:
          if str(ctx.author.id) in commandSpamWarnings and commandSpamWarnings[str(ctx.author.id)] > 2:
              
              if str(ctx.author.id) in commandTimeouts:
                  commandTimeouts[str(ctx.author.id)] = commandTimeouts[str(ctx.author.id)] + 1
              else: 
                  commandTimeouts[str(ctx.author.id)] = 1

              await botSpamLogChannel.send(f"- **<@&1327818881066336358> User TimedOut For `Command Spam In Prohibited Channels`**\n- ## MoreDetails\n```json\nUserID:{str(ctx.author.id)}\nUserName:'{ctx.author.name}'\nJson: {str(commandSpamWarnings)}\n```")
              commandSpamWarnings[str(ctx.author.id)] = 0    
              await ctx.author.timeout_for(datetime.timedelta(minutes=1 * commandTimeouts[str(ctx.author.id)]), reason="Command Spam In Prohibited Channels")
              return await ctx.respond(f"- {ctx.author.mention} **Timeout({str(1 * commandTimeouts[str(ctx.author.id)])}min), Reason: `Command Spam In Prohibited Channels`.**",ephemeral=True)  
          elif str(ctx.author.id) in commandSpamWarnings:
              commandSpamWarnings[str(ctx.author.id)] = commandSpamWarnings[str(ctx.author.id)] + 1
              return await ctx.respond(f"- {xmarkEmoji} **(x{commandSpamWarnings[str(ctx.author.id)]})Warning!, Only use this command at** <#1327823326814670888>",ephemeral=True)
          elif str(ctx.author.id) not in commandSpamWarnings:
              commandSpamWarnings[str(ctx.author.id)] = 1
              return await ctx.respond(f"- {xmarkEmoji} **(x{commandSpamWarnings[str(ctx.author.id)]})Warning!, Only use this command at** <#1327823326814670888>",ephemeral=True)  

      elif ctx.command.name not in StaffCommands and ctx.command.name != "collect" and ctx.channel_id != 1064103178020335696 and ctx.channel_id != 1325869026928496741:
          if str(ctx.author.id) in commandSpamWarnings and commandSpamWarnings[str(ctx.author.id)] > 2:
              
              if str(ctx.author.id) in commandTimeouts:
                  commandTimeouts[str(ctx.author.id)] = commandTimeouts[str(ctx.author.id)] + 1
              else:
                  commandTimeouts[str(ctx.author.id)] = 1

              await botSpamLogChannel.send(f"- **<@&1327818881066336358> User TimedOut For `Command Spam In Prohibited Channels`**\n- ## MoreDetails\n```json\nUserID:{str(ctx.author.id)}\nUserName:'{ctx.author.name}'\nJson: {str(commandSpamWarnings)}\n```")    
              commandSpamWarnings[str(ctx.author.id)] = 0
              await ctx.author.timeout_for(datetime.timedelta(minutes=1 * commandTimeouts[str(ctx.author.id)]), reason="Command Spam In Prohibited Channels")
              return await ctx.respond(f"- {ctx.author.mention} **Timeout({str(1 * commandTimeouts[str(ctx.author.id)])}min), Reason: `Command Spam In Prohibited Channels`.**",ephemeral=True)  
          elif str(ctx.author.id) in commandSpamWarnings:
              commandSpamWarnings[str(ctx.author.id)] = commandSpamWarnings[str(ctx.author.id)] + 1
              return await ctx.respond(f"- {xmarkEmoji} **(x{commandSpamWarnings[str(ctx.author.id)]})Warning!, Only use this command at** <#1064103178020335696>",ephemeral=True)  
          elif str(ctx.author.id) not in commandSpamWarnings:
              commandSpamWarnings[str(ctx.author.id)] = 1
              return await ctx.respond(f"- {xmarkEmoji} **(x{commandSpamWarnings[str(ctx.author.id)]})Warning!, Only use this command at** <#1064103178020335696>",ephemeral=True)    
          
      

      user = ctx.author
      command_name = ctx.command.name
      command_id = ctx.command.id
      options = ctx.interaction.data.get('options', [])
      args = [str(option['value']) for option in options]
      channel = bot.get_channel(commandLogsChannel)
      if command_name in StaffCommands:
        command_name = f"{command_name} [S-CMD]"
        await channel.send("- <@&1327818881066336358> **Staff Command Was Used!**")
      embed = discord.Embed(title="Command Executed By An User",description=f"```fix\nName: {user.name}\nID: {user.id}\nCommandName: {command_name}\nCommandID: {command_id}\nArguments: {str(','.join(args))}\nTime: {time.strftime('%d-%m-%Y %H:%M:%S', time.localtime())}\n```", color=discord.Color.blue())  
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
  
  
  def excludeCMD(reason: str = "This command is non functional for sometime due to some issues."):
      def decorator(func):
          @wraps(func)
          async def wrapper(ctx, *args, **kwargs):
                  await ctx.respond(f"- **{xmarkEmoji} {reason}**", ephemeral=True)
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
                  await ctx.respond(f"- **{xmarkEmoji} The command you are trying to use is in early access,You will need the __Early Access Role__ to use this command.**", ephemeral=True)
                  return
          return wrapper
      return decorator
  
  def isStaff(rank = 0):
      def decorator(func):
          @wraps(func)
          async def wrapper(ctx, *args, **kwargs):
              if not isinstance(ctx.author, discord.Member):
                  ctx.author = await ctx.guild.fetch_member(ctx.author.id)
              if rank == 0:
                roleID = 1080797844933447792
                role = discord.utils.get(ctx.author.roles, id=roleID)
              if rank == 1:
                roleID = 1080797701500837949
                role = discord.utils.get(ctx.author.roles, id=roleID)
              if rank == 2:
                roleID = 1079051010846240848
                role = discord.utils.get(ctx.author.roles, id=roleID)
              if rank == 3:
                roleID = 1079740752977993838
                role = discord.utils.get(ctx.author.roles, id=roleID)
              if rank == 4:
                roleID = 1071331526161223680
                role = discord.utils.get(ctx.author.roles, id=roleID)
              if rank == "dev":
                roleID = 1071086388709167124
                role = discord.utils.get(ctx.author.roles, id=roleID)        
              if role:
                  return await func(ctx, *args, **kwargs)
              else:
                  await ctx.respond(f"- **{xmarkEmoji} Role Required (<@&{roleID}>), You do not have the required permissions to use this command.**", ephemeral=True)
                  return
          return wrapper
      return decorator
  
  commandRateLimit = 1
  commandCoolDown = 5
  
  
  @bot.slash_command(guild_ids=servers,name='latency',description='To get the bots response time.')
  @commands.cooldown(commandRateLimit,commandCoolDown,commands.BucketType.user)
  async def latency(ctx):
      await ctx.respond(f"**Latency :** `{int(bot.latency*1000)}ms`")
  
  @bot.slash_command(guild_ids=servers,name='agent',description='Get a random agent.')
  @commands.cooldown(commandRateLimit,commandCoolDown * 2,commands.BucketType.user)
  async def agent(ctx):
     embed = discord.Embed(title="Your Agent Is -", description=f"## LOADING...\n- ...", color=discord.Color.yellow())
     embed.set_image(url="https://cdn.dribbble.com/users/756637/screenshots/2249870/slot-machine-main-2.gif")
     msg = await ctx.respond(embed=embed)
     await asyncio.sleep(1.5)
     agent = GetAgent(random.randint(0,len(GetAgentList())-1))
     embed.set_image(url=random.choice(agent['img']))
     embed.description = f"## {agent['name']}\n- {agent['info']}"
     await msg.edit(embed=embed)
  
  
  
  @bot.slash_command(guild_ids=servers, name='test_agents', description='test random agent command.')
  @commands.cooldown(commandRateLimit,commandCoolDown,commands.BucketType.user)
  @isStaff("dev")
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
         "dailyReward": "2025-01-1 03:46:05.487000+00:00",
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
  @hasAccount()
  async def balance(ctx,hidden: str = "true"):
      await ctx.defer(ephemeral=hidden.lower() not in ["false", "no"])
      data = rdb("accounts",str(ctx.author.id))
      embed = discord.Embed(title=f"Your Balance {ctx.author.display_name}", description=f"## <:_bank:1327722064307818496> : `${'{:,}'.format(data['money']['bank'])}`\n## <:_cash:1327722066660688012> : `${'{:,}'.format(data['money']['wallet'])}`\n- **Total :** `${'{:,}'.format(data['money']['wallet'] + data['money']['bank'])}`", color=discord.Color.green())
      await ctx.respond(embed=embed,ephemeral=hidden=="True")
  
  
  
  robbed = []

  async def handle_rob_removal(ctx, robbedData):
    await asyncio.sleep(120)
    user = await ctx.guild.fetch_member(robbedData['robbed'])
    if robbedData in robbed:
        robbed.remove(robbedData)
        await ctx.channel.send(f"- **{xmarkEmoji} {user.mention} You failed to find the robber in time.**")
  
  @bot.slash_command(guild_ids=servers, name='rob', description='Rob Someone.')
  @commands.cooldown(commandRateLimit,commandCoolDown * 4,commands.BucketType.user)
  @hasAccount()
  async def rob(ctx : discord.ApplicationContext,user: Annotated[discord.Member, Option(discord.Member,"Select whose wallet you want to rob")]):
      await ctx.defer(ephemeral=True)
  
      if ctx.author.id == user.id:
          return await ctx.respond(f"- **{xmarkEmoji} You cannot rob yourself.**")

      for rob in robbed:
          if rob["robbed"] == ctx.author.id:
              return await ctx.respond(f"- **{xmarkEmoji} You were just robbed so first find the robber.**")

      for rob in robbed:
          if rob["robbed"] == user.id:
              return await ctx.respond(f"- **{xmarkEmoji} {user.display_name} just got robbed so they don't have anything valuable.**")

      for rob in robbed:
          if rob["robber"] == ctx.author.id:
              return await ctx.respond(f"- **{xmarkEmoji} You just robbed someone wait sometime before you can rob again.**")
      
      if user.status.value in ['offline']: # useCase - [dnd,offline]  
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
          asyncio.create_task(handle_rob_removal(ctx, robbedData))
          await ctx.respond(f"- **{tickEmoji} You successfully robbed `${'{:,}'.format(cashFound)}`**")
          await ctx.channel.send(f"**{user.mention}, Your wallet was just robbed of `${'{:,}'.format(cashFound)}`!, You have 2min to find who it was with the command `/findrobber [name]`**")
  
      except Exception as e:
          await ctx.respond(f"- **There was an error :** `{e}`")
  
     
  @bot.slash_command(guild_ids=servers, name='findrobber', description='Find the person who robbed you.')
  @commands.cooldown(commandRateLimit,commandCoolDown,commands.BucketType.user)
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
      if robbedData["robbed"] == user.id:
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
  @hasAccount()
  async def depall(ctx : discord.ApplicationContext):
      await ctx.defer(ephemeral=True)
      walletamount = rdb("accounts",str(ctx.author.id))["money"]["wallet"]
  
      if walletamount <= 0:
          return await ctx.respond(f"- **{xmarkEmoji} You do not have any money to deposit.**")
  
      removeMoney(str(ctx.author.id),walletamount,"wallet")
      addMoney(str(ctx.author.id),walletamount,"bank")
      await ctx.respond(f"- **{tickEmoji} You successfully deposited all your money to your bank.**")
  
  


  @bot.slash_command(guild_ids=servers, name='check_inv', description="See someone's inventory.")
  @commands.cooldown(commandRateLimit, commandCoolDown * 5, commands.BucketType.user)
  @isStaff(1)
  async def check_inv(ctx: discord.ApplicationContext, user: discord.User,page: int = 1):
      await ctx.defer(ephemeral=True)
      data = rdb("accounts", str(user.id))

      if data is None:
          return await ctx.respond(f"- **{xmarkEmoji} User does not have an account.**")
      
      inventory = data["inventory"]
      await CreatePages(ctx,inventory,
      '','','',
      False,True,
      page,
      f"{user.display_name}'s Inventory",
      discord.Color.gold(),
      12,
      discord.ButtonStyle.primary)
      


  @bot.slash_command(guild_ids=servers, name='inventory', description='Open your inventory.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 3, commands.BucketType.user)
  @hasAccount()
  async def inventory(ctx: discord.ApplicationContext, hidden: str = "true", page: int = 1):
      await ctx.defer(ephemeral=hidden.lower() not in ["false", "no"])
      data = rdb("accounts", str(ctx.author.id))
      inventory = data["inventory"]

      await CreatePages(ctx,inventory,
      '','','',
      False,True,
      page,
      f"{ctx.author.display_name}'s Inventory",
      discord.Color.green(),
      12,
      discord.ButtonStyle.primary)  



  async def autocomplete_modify_inventory(ctx: discord.AutocompleteContext):
    options = list(GetItems().keys())
    return [option for option in options if ctx.value.lower() in option.lower()]  

  @bot.slash_command(guild_ids=servers, name='modify_inventory', description='Add or Remove items from a inventory.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 5, commands.BucketType.user)
  @isStaff(3)
  async def modify_inventory(ctx: discord.ApplicationContext,user: discord.User,item_id:Annotated[str,Option(str, "Choose an item", autocomplete=autocomplete_modify_inventory)],modification:int):
      await ctx.defer(ephemeral=True)
      request = updateInventory(user.id,item_id,modification)
      if request["status"] == "error":
          return await ctx.respond(f"- {xmarkEmoji} **{request['message']}**")
      if request["status"] == "success":
          return await ctx.respond(f"- {tickEmoji} **{request['message']}**")


  @bot.slash_command(guild_ids=servers, name='set_topic', description='Set current channel topic.')
  @commands.cooldown(commandRateLimit, commandCoolDown, commands.BucketType.user)
  @isStaff(2)
  async def set_topic(ctx: discord.ApplicationContext, topic: str):
      await ctx.defer(ephemeral=True)
      await ctx.channel.edit(topic=topic)
      await ctx.respond(f"- {tickEmoji} **Topic has been set to:** \n```fix\n{topic}\n```")



  @bot.slash_command(guild_ids=servers, name='collect', description='Collect your daily reward.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 25, commands.BucketType.user)
  @hasAccount()
  async def collect(ctx: discord.ApplicationContext):
    data = rdb('accounts', str(ctx.author.id))
    
    await ctx.defer(ephemeral=True)
    
    channel = bot.get_channel(1327823326814670888)
    
    if data["dailyReward"] is not None:
        try:
            daily_reward_date = parser.parse(str(data["dailyReward"])).date()
            current_date = datetime.datetime.now(datetime.timezone.utc).date()
            if daily_reward_date == current_date:
                return await ctx.respond(f"- {xmarkEmoji} **You have already collected your daily reward.**")
        except ValueError:
            await ctx.respond(f"- {xmarkEmoji} **Invalid date format in `dailyReward`.**")
            return
        
    Rewards = GetRewards()
    embed = discord.Embed(title="Daily Reward", color=discord.Color.gold())
    for reward in Rewards:
        if reward["name"] == "money":
            amount = random.randint(10,random.choice(reward["amount"]))
            embed.add_field(name="# <:_cash:1327722066660688012> Cash", value=f"`${'{:,}'.format(amount)}`", inline=True)
    
    
    if amount == 10_000:
      embed.set_image(url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/3e6f3c25140811.56342165f2d2b.gif")
    elif amount > 9_000:
      embed.set_image(url="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgIpoNexk7V40hyphenhyphencJRTOz91YM2XFWFUe51Xy62NF0905mLPsd8HZoP9l2_QyIny0c93OmnzjQS6k1D2Hz2uyDRcheIi4n571STNisvSUWCFU3orR6EBBp1Y4FIpXphkSi_epMuyqaKZMjpE/s1600/asdaasa.gif")    
    elif amount > 5_000:
      embed.set_image(url="https://media.tenor.com/5oTBpR_8aa4AAAAM/%D0%BD%D0%B5-%D0%BF%D0%BB%D0%BE%D1%85%D0%BE.gif")
    else:
      embed.set_image(url="https://media4.giphy.com/media/0laTZoLJHVHTwiag6Q/giphy.gif?cid=6c09b95211i308a8utjfrqytg7z712ltzsfdcaa2tzqzsix1&ep=v1_gifs_search&rid=giphy.gif&ct=g")  
    
    await channel.send(content=ctx.author.mention,embed=embed)

    addMoney(ctx.author.id,amount,"wallet")
    udb('accounts', str(ctx.author.id),{"dailyReward":firestore.SERVER_TIMESTAMP})
    await ctx.respond(f"- {tickEmoji} **You have collected your daily reward.**")
    
    
  async def autocomplete_modify_moneyA(ctx: discord.AutocompleteContext):
   return ["Add","Remove"]  
  async def autocomplete_modify_moneyB(ctx: discord.AutocompleteContext):
   return ["Bank","Wallet"]       
  @bot.slash_command(guild_ids=servers, name='modify_money', description='Add or Remove Money from wallet or bank of a user.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 5, commands.BucketType.user)
  @isStaff(3)
  async def modify_money(ctx: discord.ApplicationContext, user: discord.User,amount: int,action: Annotated[str,Option(str, "Choose a action", autocomplete=autocomplete_modify_moneyA)],type: Annotated[str,Option(str, "Choose a type", autocomplete=autocomplete_modify_moneyB)]):
      await ctx.defer(ephemeral=True)
      if type.lower() == "bank":
          if action.lower() == "add":
              addMoney(user.id,amount,"bank")
          elif action.lower() == "remove":
              removeMoney(user.id,amount,"bank")
          else:
              await ctx.respond(f"- {xmarkEmoji} **Invalid action.**")
              return
      elif type.lower() == "wallet":
          if action.lower() == "add":
              addMoney(user.id,amount,"wallet")
          elif action.lower() == "remove":
              removeMoney(user.id,amount,"wallet")
          else:
              await ctx.respond(f"- {xmarkEmoji} **Invalid action.**")
              return
      else:
          await ctx.respond(f"- {xmarkEmoji} **Invalid type.**")
          return
      await ctx.respond(f"- {tickEmoji} **{type} has been modified.**")


  @bot.slash_command(guild_ids=servers, name='help', description='Get a list of all commands.')
  @commands.cooldown(commandRateLimit, commandCoolDown, commands.BucketType.user)
  async def help(ctx: discord.ApplicationContext,page: int = 1):
    await ctx.defer(ephemeral=True)
    
    commands_info = [{"id":command.id,"name": command.name, "description": command.description,"staff": command.name in StaffCommands} for command in bot.commands]
    
    commands_info.sort(key=lambda cmd: (cmd["staff"] == True, cmd["name"].lower()))

    
    await CreatePages(
      ctx,
      commands_info,
      "name","description",
      False,True,False,
      page,
      "Here is a list of commands",
      discord.Color.green(),
      6,
      discord.ButtonStyle.primary)





  
  settings = rdb('about-bot','settings')
  
  if settings == None:
      raise ConnectionError(Fore.RED + "Can't fetch settings")
  elif settings["version"] != version:
      raise ConnectionRefusedError(Fore.RED + f"Version Mismatch:" + Fore.YELLOW + f"\nCurrent: {str(version).removesuffix('.0')}" + Fore.GREEN + f"\nRequired: {str(settings['version']).removesuffix('.0')}" + Fore.CYAN + f"\nDownload The Latest Version({str(settings['version']).removesuffix('.0')}) From: https://discord.gg/ZxaDHm6jc4m")
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
