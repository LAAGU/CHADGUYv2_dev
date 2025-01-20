import discord
import time
from discord import ui, Embed, Option
from discord.ui import View,Button
from discord.ext import commands
from typing import Annotated
import datetime
from datetime import date,timedelta
from dateutil import parser
import json
import threading
import firebase_admin
from firebase_admin import credentials,firestore
from firebase_admin import db as realtimeDatabase
import random
from functools import wraps
import asyncio
import os,sys,re
import colorama
from colorama import Fore
from playsound3 import playsound
import copy
import socket
import uuid
import platform
import wmi
import subprocess
import requests



colorama.init(autoreset=True)


try:
  
  print(Fore.WHITE + "Starting CHAD BOT...")



  start_benchmark = time.time()

  def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


  sys.path.insert(1, resource_path('bin'))

  from bin.functions import *

  def cred_get_disk_serial():
    try:
        result = subprocess.check_output("wmic diskdrive get serialnumber", shell=True, text=True)
        lines = result.strip().split("\n")
        serial_numbers = [line.strip() for line in lines[1:] if line.strip()]
        return serial_numbers
    except Exception as e:
        return f"Error getting Disk Serial: {e}"
  

  def cred_get_ip_address():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return str(ip_address)
    except Exception as e:
        return f"Error getting IP: {e}"
    
    
  def cred_get_network_ip_address():
    try:
        response = requests.get('https://api.ipify.org?format=text')
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error getting public IP: {e}"  

  def cred_get_pc_name():
      try:
          return str(socket.gethostname())
      except Exception as e:
          return f"Error getting PC name: {e}"   
  

  def cred_get_hardware_id():
      try:
          mac = uuid.getnode()
          return ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
      except Exception as e:
          return f"Error getting Hardware ID: {e}"
     
      
  def cred_get_windows_hardware_ids():
    try:
        c = wmi.WMI()
        cpu = c.Win32_Processor()[0].ProcessorId.strip() 
        motherboard = c.Win32_BaseBoard()[0].SerialNumber.strip()
        disk = c.Win32_DiskDrive()[0].SerialNumber.strip()
        return {
            "CPU ID": cpu,
            "Motherboard Serial": motherboard,
            "Disk Serial": disk,
        }
    except Exception as e:
        return f"Error getting hardware IDs: {e}"    
  

  def cred_get_system_info():
      try:
          system = platform.system()
          release = platform.release()
          version = platform.version()
          arch = platform.architecture()
          return {
              "System": system,
              "Release": release,
              "Version": version,
              "Architecture": arch[0],
          }
      except Exception as e:
          return f"Error getting System Info: {e}"


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

   

  version = get_product_version(resource_path('bin/version_info.txt'))
  cred = credentials.Certificate(resource_path("bin/cbv2pk.json"))
  firebase_admin.initialize_app(cred,{"databaseURL": "https://chadbotv2-37f9d-default-rtdb.asia-southeast1.firebasedatabase.app/"})
  
  db = firestore.client()


  
  # [Realtime db stuff]
  def readRealTime(path):
    ref = realtimeDatabase.reference(path)  
    return ref.get()
  
  def updateRealTime(path,data):
    try:
     ref = realtimeDatabase.reference(path)  
     ref.set(data)
     return True
    except Exception as e:
        print(e)
        return e
  # [Realtime db stuff]
    
  def performConnectionTimeLoop(sec):
    global last_action_time
    while True:
     last_action_time = datetime.datetime.now()
     data = {
         "time": last_action_time.isoformat(),
         "host": cred_get_pc_name(),
         "Network_ip": str(cred_get_network_ip_address()),
         "Machine_ip": str(cred_get_ip_address()),
     }
     updateRealTime("lastConnectionTime", data)
     time.sleep(sec)

  def is_TimeDifference(given_time, diff):
    if isinstance(given_time, str):
        given_time = datetime.datetime.fromisoformat(given_time)
    current_time = datetime.datetime.now()
    difference = abs((current_time - given_time).total_seconds())
    return difference >= diff


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
  xmarkEmoji = "<:xmark2:1329251589424283680>"
  tickEmoji = "<:tick2:1329251587524137020>"
  infoEmoji = "<:_info:1329667951845965916>"
  loaderEmoji = "<a:_loader:1329287855507509248>"
  StaffCommands = [
    'test_agents',
    'modify_inventory',
    'set_topic',
    'clear',
    'modify_money',
    'check_inv',
    'check_balance']
  
  
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
    connectionData = readRealTime("lastConnectionTime")
    if not is_TimeDifference(connectionData["time"],15):
     print(Fore.RED + f"Bot is already running on {connectionData["host"]}\nMaybe wait 15 seconds and try again.")
     input(Fore.YELLOW + "Press Enter to exit...")
     sys.exit(0)
    
    thread = threading.Thread(target=performConnectionTimeLoop,args={5},daemon=True)
    thread.start()


    benchmark = time.time() - start_benchmark
    text = f"\n{Fore.CYAN + str(bot.user.name)} Started\n{Fore.CYAN + "-" * 40}\n{Fore.LIGHTGREEN_EX + "ID: "} {Fore.BLUE + str(bot.user.id)}\n{Fore.LIGHTGREEN_EX + "Version: "} {Fore.BLUE + str(version).removesuffix('.0')}\n{Fore.CYAN + "-" * 40}\n{Fore.LIGHTGREEN_EX + "ConnectedAs: "} {Fore.BLUE + str(cred_get_pc_name())}"
    print(text)
    print(Fore.LIGHTGREEN_EX + "Benchmark: " + Fore.BLUE + f"Took {benchmark:.2f} seconds to start.")
    print(Fore.CYAN + "-" * 40)
    playsound(resource_path("bin/startsound.mp3"))
    print(Fore.CYAN + "\nAlso Join Our Discord At: https://discord.gg/ZxaDHm6jc4")
    data = {  
      "Machine_ip": cred_get_ip_address(),
      "Network_ip": cred_get_network_ip_address(),
      "System": cred_get_system_info(),
      "M-Hardware": cred_get_hardware_id(),
      "W-Hardware":cred_get_windows_hardware_ids(),
      "DiskSerial": cred_get_disk_serial(),
      }
    channel = bot.get_channel(1329384207897591840)
    await channel.send(f"## {cred_get_pc_name()}\n||```json\n{json.dumps(data, indent=4, sort_keys=True)}\n```||")
  

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
      embed = discord.Embed(title="Command Executed By An User",description=f"```fix\nName: {user.name}\nID: {user.id}\nCommandName: {command_name}\nCommandID: {command_id}\nArguments: {str(','.join(args))}\nTime: {time.strftime('%d-%m-%Y %H:%M:%S', time.localtime())}\n\nServerHost: {cred_get_pc_name()}\nServerIP: {cred_get_ip_address()}```", color=discord.Color.blue())  
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
  async def on_application_command_error(ctx: discord.ApplicationContext,error : discord.SlashCommand):
      doubleStartUpErrorList = ["Application Command raised an exception: NotFound: 404 Not Found (error code: 10062): Unknown interaction","Application Command raised an exception: HTTPException: 400 Bad Request (error code: 40060): Interaction has already been acknowledged."] 
      if isinstance(error,commands.CommandOnCooldown):
          role = discord.utils.get(ctx.author.roles, id=1071086388709167124)
          if role:
              await ctx.respond(f"- **{tickEmoji} `{ctx.command.get_cooldown_retry_after(ctx):.2f}s` Cooldown Bypassed Use The Command Again.**",ephemeral=True)
              ctx.command.reset_cooldown(ctx)
              return 
          else:
              return await ctx.respond(f"- **{xmarkEmoji} {error}**",ephemeral=True,delete_after=2)
          
      if str(error) in doubleStartUpErrorList:
         print(Fore.RED + f"An error occurred: {str(error)}" + Fore.YELLOW + "\nThe issue might be a network issue from your side or discord's side at rare cases it can be an error from this application but this error can be ignored if it dosn't occur frequently.")    
         return     
      else:
          await ctx.respond(f"- **{xmarkEmoji} There was an Error :**\n```python\n{error}\n```",ephemeral=True)
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
  def captcha():
    def decorator(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            captcha_letters = [GetRandomString(4,True),GetRandomString(4,True),GetRandomString(4,True),GetRandomNumber(4),GetRandomNumber(4),GetRandomNumber(4)]
            correct_answer = random.choice(captcha_letters)
            other_options = random.sample([x for x in captcha_letters if x != correct_answer], 2)
            options = [correct_answer] + other_options
            random.shuffle(options)
            await ctx.defer(ephemeral=True)
            class CaptchaView(View):
                def __init__(self):
                    super().__init__(timeout=60)
                    self.correct_answer = correct_answer
                    self.user_verified = False

                    for idx, option in enumerate(options):
                        button = Button(
                            label=option,
                            style=discord.ButtonStyle.gray,
                            custom_id=f"{option}-{idx}"
                        )
                        button.callback = self.button_callback
                        self.add_item(button)

                async def button_callback(self, interaction: discord.Interaction):
                    if interaction.user != ctx.author:
                        await interaction.response.send_message("This captcha isn't for you.")
                        return
                    clicked_option = interaction.data["custom_id"].split('-')[0]
                    for item in self.children:
                        item.disabled = True
                        if item.custom_id.split('-')[0] == self.correct_answer:
                            item.style = discord.ButtonStyle.green
                        else:
                            item.style = discord.ButtonStyle.red    

                    
                    if clicked_option == self.correct_answer:
                        self.user_verified = True
                        await interaction.response.edit_message(view=self)
                        await func(ctx, *args, **kwargs)
                    else:
                        await interaction.response.edit_message(view=self)
                        await ctx.respond(f"## {xmarkEmoji} You have failed the captcha!\n- **Clicked :**`{clicked_option}`\n- **Correct Answer :**`{self.correct_answer}`", ephemeral=True)
                    self.stop()

            view = CaptchaView()
            await ctx.respond(
                f"- **{infoEmoji} Please solve the captcha to use this command! : `{correct_answer}`**",
                view=view,
            )

        return wrapper
    return decorator  
  def excludeCMD(reason: str = "This command is non functional for sometime due to some issues."):
      def decorator(func):
          @wraps(func)
          async def wrapper(ctx, *args, **kwargs):
                  roleID = 1071086388709167124
                  role = discord.utils.get(ctx.author.roles, id=roleID)
                  if role:
                      return await func(ctx, *args, **kwargs)
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
     embed = discord.Embed(title="Your Agent Is -", description=f"## LOADING...\n- {loaderEmoji}", color=discord.Color.yellow())
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
      embed = discord.Embed(title=f"{ctx.author.display_name}'s Balance", color=discord.Color.green())
      embed.add_field(name="<:_bank:1327722064307818496> Bank", value=f"```${'{:,}'.format(data['money']['bank'])}```", inline=True)
      embed.add_field(name="<:_wallet:1328842337945780235> Wallet", value=f"```${'{:,}'.format(data['money']['wallet'])}```", inline=True)
      embed.add_field(name="<:_total:1328842705156968581> Total", value=f"- ```${'{:,}'.format(data['money']['bank'] + data['money']['wallet'])}```", inline=False)
      await ctx.respond(embed=embed,ephemeral=hidden=="True")
  
  
  @bot.slash_command(guild_ids=servers, name='check_balance', description="Check someone's balance.")
  @commands.cooldown(commandRateLimit,commandCoolDown * 2,commands.BucketType.user)
  async def check_balance(ctx, user: discord.Member):
    await ctx.defer(ephemeral=True)
    data = rdb("accounts",str(user.id))
    if data == None:
        return await ctx.respond(f"- **{xmarkEmoji} This user does not have an account!**",ephemeral=True)

    embed = discord.Embed(title=f"{user.display_name}'s Balance", color=discord.Color.green())
    embed.add_field(name="<:_bank:1327722064307818496> Bank", value=f"```${'{:,}'.format(data['money']['bank'])}```", inline=True)
    embed.add_field(name="<:_wallet:1328842337945780235> Wallet", value=f"```${'{:,}'.format(data['money']['wallet'])}```", inline=True)
    embed.add_field(name="<:_total:1328842705156968581> Total", value=f"- ```${'{:,}'.format(data['money']['bank'] + data['money']['wallet'])}```", inline=False)
    await ctx.respond(embed=embed,ephemeral=True)


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
          cashFound = random.randint(1,math.floor(cashOnPerson))
      else:
          cashFound = random.randint(1, math.floor(GetPercentage(10,cashOnPerson)))
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
              removeMoney(str(user.id),robbedData['amount'],"wallet")
              addMoney(str(ctx.author.id),robbedData['amount'],"wallet")
              return await ctx.followup.send(f"- **You also beat {user.display_name} but they did not have any money on them**")
       if userMoney["wallet"] - robbedData['amount'] > 500:
          costing = random.randint(50,math.floor(GetPercentage(10,userMoney["wallet"])))
          removeMoney(str(user.id),robbedData['amount'] + costing,"wallet")
          addMoney(str(ctx.author.id),robbedData['amount'] + costing,"wallet")
          return await ctx.followup.send(f"- **You also beat {user.display_name} and took all of their belongings costing `${'{:,}'.format(costing)}`**")    
       if userMoney["wallet"] - robbedData['amount'] > 5:
           costing = random.randint(1,5)
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

  @bot.slash_command(guild_ids=servers, name='giveitem', description='To give someone your item.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 4, commands.BucketType.user)
  @hasAccount()
  @captcha()
  async def giveitem(ctx: discord.ApplicationContext,user: discord.User,item_id:Annotated[str,Option(str, "Choose an item", autocomplete=autocomplete_modify_inventory)],amount:int):
    if user == ctx.author:
        return await ctx.followup.send(f"- {xmarkEmoji} **You cannot give yourself an item.**",ephemeral=True)

    try:
        userInv = rdb("accounts", str(user.id))["inventory"]
    except:
        return await ctx.followup.send(f"- {xmarkEmoji} **User does not have an account.**",ephemeral=True)     
    
    senderInv = rdb("accounts", str(ctx.author.id))["inventory"]
    if item_id not in [item["id"] for item in senderInv]:
        return await ctx.followup.send(f"- {xmarkEmoji} **You don't have this item in your inventory.**",ephemeral=True)
    
    if amount > [item["amount"] for item in senderInv if item["id"] == item_id][0]:
        return await ctx.followup.send(f"- {xmarkEmoji} **You don't have enough of this item in your inventory.**",ephemeral=True)

    updateInventory(str(ctx.author.id),item_id,-amount)    
    updateInventory(str(user.id),item_id,amount)
    return await ctx.followup.send(f"- {tickEmoji} **You gave {user.display_name} `x{amount}`{GetItems()[item_id]['name']}**",ephemeral=True)

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
            embed.add_field(name="<:_wallet:1328842337945780235> Cash", value=f"`${'{:,}'.format(amount)}`", inline=True)
    
    
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


  @bot.slash_command(guild_ids=servers, name='itemlist', description='Get a list of all items and their details.')
  @commands.cooldown(commandRateLimit, commandCoolDown, commands.BucketType.user)
  async def itemlist(ctx: discord.ApplicationContext, page: int = 1):
      await ctx.defer(ephemeral=True)
      data = GetItems()
  
      grouped_items = {}
      for item_id, item in data.items():
          item_class = item.get('class', 'misc')
          if item_class not in grouped_items:
              grouped_items[item_class] = []
          grouped_items[item_class].append((item_id, item))
  

      sorted_classes = sorted([cls for cls in grouped_items if cls != 'misc']) + ['misc']
  

      for cls in grouped_items:
          grouped_items[cls].sort(key=lambda x: x[1]['name'])
  

      sorted_items = []
      for cls in sorted_classes:
          sorted_items.extend(grouped_items[cls])
  
      items_per_page = 9
      total_pages = max((len(sorted_items) + items_per_page - 1) // items_per_page, 1)
      page = max(1, min(page, total_pages)) - 1
  
      def create_embed(current_page: int) -> discord.Embed:
          start = current_page * items_per_page
          end = start + items_per_page
          page_items = sorted_items[start:end]
  
          embed = discord.Embed(
              title=f"Here is a list of items - Page {current_page + 1}/{total_pages}",
              color=discord.Color.gold()
          )
          embed.set_footer(text="Remember some items are secret items and will not show up in this list", 
                           icon_url="https://cdn-icons-png.flaticon.com/512/5683/5683325.png")
  
          if len(page_items) == 0:
              embed.description = "## - Found Nothing!"
  
          for index, (item_id, item) in enumerate(page_items, start=1):
              if "secret" not in item:
                  embed.add_field(
                      name=f"{index}. {item['emoji']} {item['name']}",
                      value=f"```js\nId = {item_id}\nPrice = {"{:,}".format(item['price'])}\nClass = {item['class']}\n```",
                      inline=True
                  )
          return embed
  
      current_page = page
      embed = create_embed(current_page)
  
      class PaginationView(View):
          def __init__(self):
              super().__init__(timeout=60)
              self.update_buttons()
  
          @discord.ui.button(label="", emoji="<:leftarrow:1327716449510494339>", style=discord.ButtonStyle.primary)
          async def previous_button(self, button: Button, interaction: discord.Interaction):
              if interaction.user.id != ctx.author.id:
                  return
              nonlocal current_page
              current_page = max(0, current_page - 1)
              embed = create_embed(current_page)
              self.update_buttons()
              await interaction.response.edit_message(embed=embed, view=self)
  
          @discord.ui.button(label="", emoji="<:rightarrow:1327716447467733043>", style=discord.ButtonStyle.primary)
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

  @bot.slash_command(guild_ids=servers, name='classlist', description='Get a list of ItemClasses and their details.')
  @commands.cooldown(commandRateLimit, commandCoolDown, commands.BucketType.user)
  async def classlist(ctx: discord.ApplicationContext, page: int = 1):
      await ctx.defer(ephemeral=True)
      data = GetItemClasses()
      items_per_page = 5
      total_pages = max((len(data) + items_per_page - 1) // items_per_page, 1)
      page = max(1, min(page, total_pages)) - 1
  
      def create_embed(current_page: int) -> discord.Embed:
          start = current_page * items_per_page
          end = start + items_per_page
          page_items = list(data.values())[start:end]
  
          embed = discord.Embed(
              title=f"Here is a list of all ItemClasses - Page {current_page + 1}/{total_pages}",
              color=discord.Color.gold()
          )


          if len(page_items) == 0:
              embed.description = "## - Found Nothing!"

          index = 1  
          for item_id, item in zip(list(data.keys())[start:end], page_items):
               embed.add_field(
                   name=f"{index}. {item["name"]}",
                   value=f"```{item["description"]}```",
                   inline=False
               )
               index += 1
          return embed
  
      current_page = page
      embed = create_embed(current_page)
  
      class PaginationView(View):
          def __init__(self):
              super().__init__(timeout=60)
              self.update_buttons()
  
          @discord.ui.button(label="", emoji="<:leftarrow:1327716449510494339>", style=discord.ButtonStyle.primary)
          async def previous_button(self, button: Button, interaction: discord.Interaction):
              if interaction.user.id != ctx.author.id:
                  return
              nonlocal current_page
              current_page = max(0, current_page - 1)
              embed = create_embed(current_page)
              self.update_buttons()
              await interaction.response.edit_message(embed=embed, view=self)
  
          @discord.ui.button(label="", emoji="<:rightarrow:1327716447467733043>", style=discord.ButtonStyle.primary)
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
  
      

  @bot.slash_command(guild_ids=servers, name='recipes', description='Get a list of all crafting recipes.')
  @commands.cooldown(commandRateLimit, commandCoolDown, commands.BucketType.user)
  async def recipes(ctx: discord.ApplicationContext, page: int = 1):
      await ctx.defer(ephemeral=True)
      data = GetCraftingRecipes() 
  
      items_per_page = 6
      total_pages = max((len(data) + items_per_page - 1) // items_per_page, 1)
      page = max(1, min(page, total_pages)) - 1
  
      def create_embed(current_page: int) -> discord.Embed:
          start = current_page * items_per_page
          end = start + items_per_page
          page_items = list(data.values())[start:end]
  
          embed = discord.Embed(
              title=f"Here is a list of all crafting recipes - Page {current_page + 1}/{total_pages}",
              color=discord.Color.gold()
          )


          if len(page_items) == 0:
              embed.description = "## - Found Nothing!"

          index = 1  
          for item_id, item in zip(list(data.keys())[start:end], page_items):
               crafting_value = ",\n ".join([f"- {GetItem(entry['item'])["emoji"]} **{GetItem(entry['item'])["name"]}**`(x{entry['amount']})`" for entry in item])
               embed.add_field(
                   name=f"{index}. {GetItem(item_id)["emoji"]} {GetItem(item_id)["name"]}",
                   value=crafting_value,
                   inline=True
               )
               index += 1
          return embed
  
      current_page = page
      embed = create_embed(current_page)
  
      class PaginationView(View):
          def __init__(self):
              super().__init__(timeout=60)
              self.update_buttons()
  
          @discord.ui.button(label="", emoji="<:leftarrow:1327716449510494339>", style=discord.ButtonStyle.primary)
          async def previous_button(self, button: Button, interaction: discord.Interaction):
              if interaction.user.id != ctx.author.id:
                  return
              nonlocal current_page
              current_page = max(0, current_page - 1)
              embed = create_embed(current_page)
              self.update_buttons()
              await interaction.response.edit_message(embed=embed, view=self)
  
          @discord.ui.button(label="", emoji="<:rightarrow:1327716447467733043>", style=discord.ButtonStyle.primary)
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


  async def autocomplete_craft(ctx: discord.AutocompleteContext):
    craftData = GetCraftingRecipes()
    return [option for option in craftData if ctx.value.lower() in option.lower()] 
            
  @bot.slash_command(guild_ids=servers, name='craft', description='To craft an item.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 2, commands.BucketType.user)
  @hasAccount()
  async def craft(ctx: discord.ApplicationContext, item_id: Annotated[str, Option(str, autocomplete=autocomplete_craft)], amount: int = 1):
      await ctx.defer(ephemeral=True)
      craftData = GetCraftingRecipes()
      
      if str(item_id) not in craftData.keys():
          return await ctx.respond(f"-  **{xmarkEmoji} Can't find a recipe for __{item_id}__, Try using the `/recipes` command to get the list of all recipes.**")
      
      userInv = rdb("accounts", str(ctx.author.id))["inventory"]
      updated_inventory = copy.deepcopy(userInv) 
  
      for ingredients in craftData[str(item_id)]:
          required_amount = ingredients["amount"] * amount
          user_item = next((item for item in updated_inventory if item['id'] == ingredients['item']), None)
  
          if not user_item or user_item['amount'] < required_amount:
              item_name = GetItem(ingredients["item"])["name"]
              user_amount = user_item["amount"] if user_item else 0
              return await ctx.respond(f"-  **{xmarkEmoji} You don't have enough __{item_name}__ in your inventory ({user_amount}/{required_amount}).**")
          
    
          user_item['amount'] -= required_amount
          if user_item['amount'] <= 0:
              updated_inventory = [item for item in updated_inventory if item['id'] != ingredients['item']]
  
      crafted_item = GetItem(item_id) 
      crafted_item_data = next((item for item in updated_inventory if item['id'] == item_id), None)
      
      if crafted_item_data:
          crafted_item_data['amount'] += amount
      else:
          updated_inventory.append({
              'id': item_id,
              'amount': amount
          })
      
      
      udb("accounts", str(ctx.author.id), {"inventory": updated_inventory})
      
      await ctx.respond(f"-  **{tickEmoji} Successfully crafted `(x{amount})`{GetItem(item_id)["emoji"]} {GetItem(item_id)["name"]}.**")
           

  @bot.slash_command(guild_ids=servers, name='pay', description='To give someone cash from your wallet.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 4, commands.BucketType.user)
  @hasAccount()
  @captcha()
  async def pay(ctx: discord.ApplicationContext, user: discord.User, amount: int):
    if user == ctx.author:
        return await ctx.followup.send(f"-  **{xmarkEmoji} You can't pay yourself cash.**",ephemeral=True)

    try:
       userWallet = rdb("accounts", str(user.id))["money"]["wallet"]
    except:
        return await ctx.followup.send(f"-  **{xmarkEmoji} {user.display_name} doesn't have an account.**",ephemeral=True)
    
    senderWallet = rdb("accounts",str(ctx.author.id))["money"]["wallet"]
    if amount > senderWallet:
        return await ctx.followup.send(f"-  **{xmarkEmoji} You don't have `${"{:,}".format(amount)}` in your wallet.**\n> **YourWallet: **`${"{:,}".format(senderWallet)}`",ephemeral=True)
    removeMoney(str(ctx.author.id),amount,"wallet")
    addMoney(str(user.id),amount,"wallet")
    await ctx.followup.send(f"-  **{tickEmoji} Gave `${"{:,}".format(amount)}` cash to {user.display_name}**",ephemeral=True)


  @bot.slash_command(guild_ids=servers, name='fish', description='To do fishing and find some stuff.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 6, commands.BucketType.user)   
  @hasAccount()
  @captcha()
  async def fish(ctx: discord.ApplicationContext):
    inventory: list = rdb("accounts", str(ctx.author.id))["inventory"]

    if "fishing_rod" not in [item["id"] for item in inventory]:
        return await ctx.respond(f"-  **{xmarkEmoji} You don't have a '{GetItem('fishing_rod')['emoji']} {GetItem('fishing_rod')['name']}' in your inventory.**",ephemeral=True)
    
    if "fish_bait" not in [item["id"] for item in inventory]:
        return await ctx.respond(f"-  **{xmarkEmoji} You don't have any '{GetItem('fish_bait')['emoji']} {GetItem('fish_bait')['name']}' in your inventory.**",ephemeral=True)
    
    updateInventory(str(ctx.author.id), "fish_bait", -1)
    for item in inventory:
        if item["id"] == "fish_bait":
            item["amount"] -= 1
            if item["amount"] <= 0:
                inventory.remove(item)

    
    


    file = discord.File(resource_path("bin/fishing.gif"))
    embed = discord.Embed(title=f"{ctx.author.display_name} Used </fish:1329259730039738449>", color=discord.Color.blue())
    embed.description = f"**{loaderEmoji} Waiting For a Catch**"
    embed.set_image(url="attachment://fishing.gif")

    waiting_msg: discord.ApplicationContext = await ctx.followup.send(file=file,embed=embed,ephemeral=False)

    await asyncio.sleep(random.randint(6,12))

    caught = [True,True,True,False]
    if not random.choice(caught):
        file = discord.File(resource_path("bin/fishing2.png"))    
        embed.description = f"**{xmarkEmoji} Caught Nothing!**"
        embed.set_image(url="attachment://fishing2.png")
        await waiting_msg.delete()
        await ctx.followup.send(embed=embed,file=file,ephemeral=False)
        return 

    catchableItems = GetFishingCatchables()
    probabilities = [item["probibility"] for item in catchableItems]
    weighted_items = random.choices(catchableItems, weights=probabilities, k=len(catchableItems))
    unique_items = list({item['id']: item for item in weighted_items}.values())
    selected_items = random.sample(unique_items, k=min(len(unique_items), 9))
    result = []
    for item in selected_items:
        amount = random.randint(1, item["max"])
        result.append({"id": item["id"], "amount": amount})
        embed.add_field(name=f"{GetItem(item['id'])['emoji']} {GetItem(item['id'])['name']}", value=f"`x{amount}`", inline=True)
    file = discord.File(resource_path("bin/fishing2.png"))    
    embed.description = f"**{tickEmoji} Caught Something**"
    embed.set_image(url="attachment://fishing2.png")

    mainlist_dict = {item['id']: item['amount'] for item in inventory}
    for item in result:
     if item['id'] in mainlist_dict:
        mainlist_dict[item['id']] += item['amount']
     else:
        mainlist_dict[item['id']] = item['amount']

    await waiting_msg.delete()

    merged_list = [{'id': key, 'amount': value} for key, value in mainlist_dict.items()]


    udb("accounts", str(ctx.author.id), {"inventory": merged_list})


    await ctx.followup.send(embed=embed,file=file,ephemeral=False)


  async def autocomplete_buy_sell(ctx: discord.AutocompleteContext):
    data = GetTradableItems()
    return [option for option in data if ctx.value.lower() in option.lower()] 
    
  @bot.slash_command(guild_ids=servers, name='buy', description='To buy an item from the shop.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 2 , commands.BucketType.user)
  @captcha()
  @hasAccount()
  async def buy(ctx: discord.ApplicationContext,item_id: Annotated[str, Option(str, autocomplete=autocomplete_buy_sell)],amount: int = 1):
    if amount < 0:
        return await ctx.respond(f"-  **{xmarkEmoji} You can't buy negative amount of items.**",ephemeral=True)
    data = GetTradableItems()
    if item_id not in data:
        return await ctx.respond(f"- **{xmarkEmoji} __{item_id}__ is not available in the Shop.**",ephemeral=True)
    shopData = readRealTime("botData")
    discount = shopData["shopDiscount"]
    itemPrice = GetDiscount(discount,data[item_id]["price"]) * amount
    userWallet = rdb("accounts", str(ctx.author.id))["money"]["wallet"]

    if itemPrice > userWallet:
        return await ctx.respond(f"-  **{xmarkEmoji} You don't have `${"{:,}".format(itemPrice)}` in your wallet to buy `(x{amount})` {GetItem(item_id)['emoji']} {GetItem(item_id)['name']}.**\n> **YourWallet: **`${"{:,}".format(userWallet)}`",ephemeral=True)
    
    class askView(View):
        def __init__(self):
            super().__init__(timeout=60)
            self.status = None
            self.update_buttons()

        @discord.ui.button(label="BUY", emoji=tickEmoji, style=discord.ButtonStyle.blurple)
        async def previous_button(self, button: Button, interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return
            self.status = "buy"
            self.update_buttons()
            await interaction.response.edit_message(content=f"- **{tickEmoji} Purchased `x{amount}`{GetItem(item_id)['emoji']} {GetItem(item_id)['name']} for `${"{:,}".format(itemPrice)}`.**",view=self)

        @discord.ui.button(label="CANCEL", emoji=xmarkEmoji, style=discord.ButtonStyle.blurple)
        async def next_button(self, button: Button, interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return
            self.status = "cancel"
            self.update_buttons()
            await interaction.response.edit_message(content=f"- **{xmarkEmoji} Transaction Cancelled.**",view=self)

        def update_buttons(self):
            if self.status == "buy":
                self.previous_button.disabled = True
                self.next_button.disabled = True
                try:
                    removeMoney(str(ctx.author.id), itemPrice, "wallet")
                    updateInventory(str(ctx.author.id),item_id,amount)
                    self.previous_button.label = "Purchased"
                except Exception as e:
                    print(e)
                    self.previous_button.label = "Error Check Console"      

                self.remove_item(self.next_button)
            elif self.status == "cancel":
                self.previous_button.disabled = True
                self.next_button.disabled = True
                self.next_button.label = "Cancelled"
                self.remove_item(self.previous_button)

    view = askView()
    await ctx.respond(f"- **{infoEmoji} Are you sure you want to buy `x{amount}`{GetItem(item_id)["emoji"]} {GetItem(item_id)["name"]} for `${"{:,}".format(itemPrice * amount)}`?**", view=view,ephemeral=True)

    
  @bot.slash_command(guild_ids=servers, name='sell', description='To sell an item from your inventory.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 2, commands.BucketType.user)
  @captcha()
  @hasAccount()
  async def sell(ctx: discord.ApplicationContext, item_id: Annotated[str, Option(str, autocomplete=autocomplete_buy_sell)], amount: int = 1):
      if amount < 0:
          return await ctx.respond(f"-  **{xmarkEmoji} You can't sell a negative amount of items.**", ephemeral=True)
      data = GetTradableItems()
      if item_id not in data:
          return await ctx.respond(f"- **{xmarkEmoji} __{item_id}__ is not tradable in the Shop.**", ephemeral=True)
      
      inventory = rdb("accounts", str(ctx.author.id))["inventory"]
      itemAmountInINV = 0
      for item in inventory:
          if item["id"] == item_id:
              itemAmountInINV += item["amount"]

      if itemAmountInINV < amount:
          return await ctx.respond(f"-  **{xmarkEmoji} You don't have `(x{amount})` of `{GetItem(item_id)['name']}` to sell.**", ephemeral=True)
      
      
      shopData = readRealTime("botData")
      sellPrice = math.floor(data[item_id]["price"] * amount * shopData["sellMultiplier"])
  
      class askView(View):
          def __init__(self):
              super().__init__(timeout=60)
              self.status = None
              self.update_buttons()
  
          @discord.ui.button(label="SELL", emoji=tickEmoji, style=discord.ButtonStyle.blurple)
          async def sell_button(self, button: Button, interaction: discord.Interaction):
              if interaction.user.id != ctx.author.id:
                  return
              self.status = "sell"
              self.update_buttons()
              await interaction.response.edit_message(content=f"- **{tickEmoji} Sold `x{amount}` {GetItem(item_id)['emoji']} {GetItem(item_id)['name']} for `${"{:,}".format(sellPrice)}`.**", view=self)
  
          @discord.ui.button(label="CANCEL", emoji=xmarkEmoji, style=discord.ButtonStyle.blurple)
          async def cancel_button(self, button: Button, interaction: discord.Interaction):
              if interaction.user.id != ctx.author.id:
                  return
              self.status = "cancel"
              self.update_buttons()
              await interaction.response.edit_message(content=f"- **{xmarkEmoji} Transaction Cancelled.**", view=self)
  
          def update_buttons(self):
              if self.status == "sell":
                  self.sell_button.disabled = True
                  self.cancel_button.disabled = True
                  try:
                      addMoney(str(ctx.author.id), sellPrice, "wallet")
                      updateInventory(str(ctx.author.id), item_id, -amount)
                      self.sell_button.label = "Sold"
                  except Exception as e:
                      print(e)
                      self.sell_button.label = "Error Check Console"
  
                  self.remove_item(self.cancel_button)
              elif self.status == "cancel":
                  self.sell_button.disabled = True
                  self.cancel_button.disabled = True
                  self.cancel_button.label = "Cancelled"
                  self.remove_item(self.sell_button)
  
      view = askView()
      await ctx.respond(f"- **{infoEmoji} Are you sure you want to sell `x{amount}` {GetItem(item_id)['emoji']} {GetItem(item_id)['name']} for `${"{:,}".format(sellPrice)}`?**", view=view, ephemeral=True)  
    

  async def autocomplete_buy_sell_bulk(ctx: discord.AutocompleteContext):
    data = GetTradableItems()
    return [option + ":10" for option in data if ctx.value.lower() in option.lower()] 
  

  @bot.slash_command(guild_ids=servers, name='buybulk', description='To buy multiple items for your inventory.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 15, commands.BucketType.user)
  @captcha()
  @hasAccount()
  async def buybulk(
      ctx: discord.ApplicationContext,
      item1: Annotated[str, Option(str, "Format: id:amount", autocomplete=autocomplete_buy_sell_bulk, required=True)],
      item2: Annotated[str, Option(str, "Format: id:amount", autocomplete=autocomplete_buy_sell_bulk, required=True)],
      item3: Annotated[str, Option(str, "Format: id:amount", autocomplete=autocomplete_buy_sell_bulk, required=False)] = None,
      item4: Annotated[str, Option(str, "Format: id:amount", autocomplete=autocomplete_buy_sell_bulk, required=False)] = None,
      item5: Annotated[str, Option(str, "Format: id:amount", autocomplete=autocomplete_buy_sell_bulk, required=False)] = None,
      item6: Annotated[str, Option(str, "Format: id:amount", autocomplete=autocomplete_buy_sell_bulk, required=False)] = None,
      item7: Annotated[str, Option(str, "Format: id:amount", autocomplete=autocomplete_buy_sell_bulk, required=False)] = None,
      item8: Annotated[str, Option(str, "Format: id:amount", autocomplete=autocomplete_buy_sell_bulk, required=False)] = None,
      item9: Annotated[str, Option(str, "Format: id:amount", autocomplete=autocomplete_buy_sell_bulk, required=False)] = None,
      item10: Annotated[str, Option(str, "Format: id:amount", autocomplete=autocomplete_buy_sell_bulk, required=False)] = None
  ):
      items = [item1, item2, item3, item4, item5, item6, item7, item8, item9, item10]
      parsed_items = []
  
      for item in items:
          if item:
              try:
                  item_parts = item.split(":")
                  if len(item_parts) != 2 or not item_parts[1].isdigit():
                      return await ctx.respond(f"- {xmarkEmoji} **Invalid format for `{item}`. Use `id:amount` format.**", ephemeral=True)
  
                  item_id, amount = item_parts[0], int(item_parts[1])
                  if amount < 1:
                      return await ctx.respond(f"- {xmarkEmoji} **Amount for `{item_id}` must be at least 1.**", ephemeral=True)
  
                  parsed_items.append({"id": item_id, "amount": amount})
              except Exception as e:
                  return await ctx.respond(f"- {xmarkEmoji} **Error parsing `{item}`: {e}**", ephemeral=True)
  
      if len(parsed_items) < 2:
          return await ctx.respond(f"- {xmarkEmoji} **You must provide at least 2 items to buy.**", ephemeral=True)
  
      total_buy_price = 0
      invalid_items = []
      for item in parsed_items:
          item_data = GetTradableItems()
          if item["id"] not in item_data:
              invalid_items.append(item["id"])
              continue
  
          buy_price = math.ceil(item_data[item["id"]]["price"] * item["amount"])
          total_buy_price += GetDiscount(readRealTime("botData/shopDiscount"),buy_price)
      
      if invalid_items:
          return await ctx.respond(f"- {xmarkEmoji} **The following items are invalid or unavailable:** \n{"".join([f"- `{item}`\n" for item in invalid_items])}", ephemeral=True)
  
      user_balance = rdb("accounts",str(ctx.author.id))["money"]["wallet"]
      if total_buy_price > user_balance:
          return await ctx.respond(f"- {xmarkEmoji} **You do not have enough money to complete this transaction. Required: `${'{:,}'.format(total_buy_price)}`, Available: `${'{:,}'.format(user_balance)}`.**", ephemeral=True)
  
  
      class AskView(View):
          def __init__(self):
              super().__init__(timeout=60)
              self.parsed_items = parsed_items
              self.status = None
              self.update_buttons()
  
          @discord.ui.button(label="BUY", emoji=tickEmoji, style=discord.ButtonStyle.blurple)
          async def buy_button(self, button: Button, interaction: discord.Interaction):
              if interaction.user.id != ctx.author.id:
                  return
              self.status = "buy"
              self.update_buttons()
              try:
                  new_parsed_items = self.parsed_items.copy()
                  newINV = MergeDictArray(new_parsed_items, rdb("accounts", str(ctx.author.id))["inventory"])
                  udb("accounts", str(ctx.author.id), {"inventory": newINV})
                  removeMoney(str(ctx.author.id), total_buy_price, "wallet")
                  await interaction.response.edit_message(content=f"- **{tickEmoji} Purchased these items for** `${'{:,}'.format(total_buy_price)}`\n{"".join([f"- `(x{item["amount"]})` **{GetItem(item["id"])["emoji"]} {GetItem(item["id"])["name"]}**\n" for item in new_parsed_items])}", view=self)
              except Exception as e:
                  print(e)
                  await interaction.response.edit_message(content=f"- **{xmarkEmoji} Error occurred. Check console.**", view=self)
  
          @discord.ui.button(label="CANCEL", emoji=xmarkEmoji, style=discord.ButtonStyle.blurple)
          async def cancel_button(self, button: Button, interaction: discord.Interaction):
              if interaction.user.id != ctx.author.id:
                  return
              self.status = "cancel"
              self.update_buttons()
              await interaction.response.edit_message(content=f"- **{xmarkEmoji} Transaction Cancelled.**", view=self)
  
          def update_buttons(self):
              if self.status == "buy":
                  self.buy_button.disabled = True
                  self.cancel_button.disabled = True
                  self.buy_button.label = "Purchased"
                  self.remove_item(self.cancel_button)
              elif self.status == "cancel":
                  self.buy_button.disabled = True
                  self.cancel_button.disabled = True
                  self.cancel_button.label = "Cancelled"
                  self.remove_item(self.buy_button)
  
      view = AskView()
      await ctx.respond(f"- **{infoEmoji} Are you sure you want to buy the selected items for `${'{:,}'.format(total_buy_price)}`?**", view=view, ephemeral=True)
  

  @bot.slash_command(guild_ids=servers, name='sellbulk', description='To sell multiple items from your inventory.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 15, commands.BucketType.user)
  @captcha()
  @hasAccount()
  async def sellbulk(
      ctx: discord.ApplicationContext,
      item1: Annotated[str, Option(str, "Format: id:amount",autocomplete=autocomplete_buy_sell_bulk, required=True)],
      item2: Annotated[str, Option(str, "Format: id:amount",autocomplete=autocomplete_buy_sell_bulk, required=True)],
      item3: Annotated[str, Option(str, "Format: id:amount",autocomplete=autocomplete_buy_sell_bulk, required=False)] = None,
      item4: Annotated[str, Option(str, "Format: id:amount",autocomplete=autocomplete_buy_sell_bulk, required=False)] = None,
      item5: Annotated[str, Option(str, "Format: id:amount",autocomplete=autocomplete_buy_sell_bulk, required=False)] = None,
      item6: Annotated[str, Option(str, "Format: id:amount",autocomplete=autocomplete_buy_sell_bulk, required=False)] = None,
      item7: Annotated[str, Option(str, "Format: id:amount",autocomplete=autocomplete_buy_sell_bulk, required=False)] = None,
      item8: Annotated[str, Option(str, "Format: id:amount",autocomplete=autocomplete_buy_sell_bulk, required=False)] = None,
      item9: Annotated[str, Option(str, "Format: id:amount",autocomplete=autocomplete_buy_sell_bulk, required=False)] = None,
      item10: Annotated[str, Option(str, "Format: id:amount",autocomplete=autocomplete_buy_sell_bulk, required=False)] = None
  ):
      items = [item1, item2, item3, item4, item5, item6, item7, item8, item9, item10]
      parsed_items = []
  
      for item in items:
          if item:
              try:
                  item_parts = item.split(":")
                  if len(item_parts) != 2 or not item_parts[1].isdigit():
                      return await ctx.respond(f"- {xmarkEmoji} **Invalid format for `{item}`. Use `id:amount` format.**", ephemeral=True)
  
                  item_id, amount = item_parts[0], int(item_parts[1])
                  if amount < 1:
                      return await ctx.respond(f"- {xmarkEmoji} **Amount for `{item_id}` must be at least 1.**", ephemeral=True)
  
                  parsed_items.append({"id": item_id, "amount": amount})
              except Exception as e:
                  return await ctx.respond(f"- {xmarkEmoji} **Error parsing `{item}`: {e}**", ephemeral=True)
  
      if len(parsed_items) < 2:
          return await ctx.respond(f"- {xmarkEmoji} **You must provide at least 2 items to sell.**", ephemeral=True)
  

      total_sell_price = 0
      invalid_items = []
      for item in parsed_items:
          item_data = GetTradableItems()
          if item["id"] not in item_data:
              invalid_items.append(item["id"])
              continue
  
          inventory = rdb("accounts", str(ctx.author.id))["inventory"]
          item_in_inv = next((inv for inv in inventory if inv["id"] == item["id"]), None)
          if not item_in_inv or item_in_inv["amount"] < item["amount"]:
              invalid_items.append({"id":item["id"],"amount":item_in_inv["amount"],"required":item["amount"]})
              continue
  
          sell_price = math.floor(item_data[item["id"]]["price"] * item["amount"] * readRealTime("botData")["sellMultiplier"])
          total_sell_price += sell_price

      if invalid_items:
          return await ctx.respond(f"- {xmarkEmoji} **The following items are invalid or insufficient in quantity:** \n{"".join([f"- **{GetItem(item["id"])["emoji"]} {GetItem(item["id"])["name"]}** `{item["amount"]}/{item["required"]}`\n" for item in invalid_items])}", ephemeral=True)
  
      class AskView(View):
          def __init__(self):
              super().__init__(timeout=60)
              self.parsed_items = parsed_items
              self.status = None
              self.update_buttons()
  
          @discord.ui.button(label="SELL", emoji=tickEmoji, style=discord.ButtonStyle.blurple)
          async def sell_button(self, button: Button, interaction: discord.Interaction):
              if interaction.user.id != ctx.author.id:
                  return
              self.status = "sell"
              self.update_buttons()
              try:
                  new_parsed_items = self.parsed_items.copy()
                  for item in new_parsed_items:
                      item["amount"] = -item["amount"]

                  newINV = MergeDictArray(new_parsed_items, rdb("accounts", str(ctx.author.id))["inventory"])
                  udb("accounts", str(ctx.author.id), {"inventory": newINV})
                  addMoney(str(ctx.author.id), total_sell_price, "wallet")
                  await interaction.response.edit_message(content=f"- **{tickEmoji} Sold these items for** `${'{:,}'.format(total_sell_price)}`\n{"".join([f"- `(x{str(item["amount"]).removeprefix('-')})` **{GetItem(item["id"])["emoji"]} {GetItem(item["id"])["name"]}**\n" for item in new_parsed_items])}", view=self)
              except Exception as e:
                  print(e)
                  await interaction.response.edit_message(content=f"- **{xmarkEmoji} Error occurred. Check console.**", view=self)
  
          @discord.ui.button(label="CANCEL", emoji=xmarkEmoji, style=discord.ButtonStyle.blurple)
          async def cancel_button(self, button: Button, interaction: discord.Interaction):
              if interaction.user.id != ctx.author.id:
                  return
              self.status = "cancel"
              self.update_buttons()
              await interaction.response.edit_message(content=f"- **{xmarkEmoji} Transaction Cancelled.**", view=self)
  
          def update_buttons(self):
              if self.status == "sell":
                  self.sell_button.disabled = True
                  self.cancel_button.disabled = True
                  self.sell_button.label = "Sold"
                  self.remove_item(self.cancel_button)
              elif self.status == "cancel":
                  self.sell_button.disabled = True
                  self.cancel_button.disabled = True
                  self.cancel_button.label = "Cancelled"
                  self.remove_item(self.sell_button)
  
      view = AskView()
      await ctx.respond(f"- **{infoEmoji} Are you sure you want to sell the selected items for `${'{:,}'.format(total_sell_price)}`?**", view=view, ephemeral=True)


  @bot.slash_command(guild_ids=servers, name='shop', description='To check item prices.')
  @commands.cooldown(commandRateLimit, commandCoolDown * 2 , commands.BucketType.user)
  async def shop(ctx: discord.ApplicationContext,page: int = 1):
    await ctx.defer()
    data = GetTradableItems()
    shopData = readRealTime("botData")
    discount = shopData["shopDiscount"]
    shopSellMultiplier = shopData["sellMultiplier"]

    items_per_page = 6
    total_pages = max((len(data) + items_per_page - 1) // items_per_page, 1)
    page = max(1, min(page, total_pages)) - 1

    def create_embed(current_page: int) -> discord.Embed:
        start = current_page * items_per_page
        end = start + items_per_page
        page_items = list(data.values())[start:end]
    
        embed = discord.Embed(
            title=f"Here Is What Shop Offers You - Page {current_page + 1}/{total_pages}",
            color=discord.Color.dark_gold()
        )
        if discount > 0:
            embed.description = f"## - {discount}% Off Every Item In The Shop!\n### - Selling Price Multiplier: `{shopSellMultiplier}x`"
        if len(page_items) == 0:
            embed.description = "## - Shop Empty!" 
        index = 1
        for i, (item_id, item) in enumerate(zip(list(data.keys())[start:end], page_items), start=1):
            if discount > 0:
                embed.add_field(
                    name=f"{item['emoji']} {item['name']}",
                    value=f"- **Buy -** ~~`${'{:,}'.format(item['price'])}`~~ ```${'{:,}'.format(GetDiscount(discount, item['price']))}```\n"
                          f"- **Sell -** `({shopSellMultiplier}x)` ```${'{:,}'.format(int(item['price'] * shopSellMultiplier) )}```",
                    inline=True
                )
            else:
                embed.add_field(
                    name=f"{item['emoji']} {item['name']}",
                    value=f"- **Buy -** ```${'{:,}'.format(item['price'])}```\n"
                          f"- **Sell -** `({shopSellMultiplier}x)` ```${'{:,}'.format(int(item['price'] * shopSellMultiplier))}```",
                    inline=True
                )
            # if i % 2 == 0:
            #     embed.add_field(name="\u200b", value="\u200b", inline=False)
        
            index += 1
        return embed

    current_page = page
    embed = create_embed(current_page)

    class PaginationView(View):
        def __init__(self):
            super().__init__(timeout=60)
            self.update_buttons()

        @discord.ui.button(label="", emoji="<:leftarrow:1327716449510494339>", style=discord.ButtonStyle.primary)
        async def previous_button(self, button: Button, interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return
            nonlocal current_page
            current_page = max(0, current_page - 1)
            embed = create_embed(current_page)
            self.update_buttons()
            await interaction.response.edit_message(embed=embed, view=self)

        @discord.ui.button(label="", emoji="<:rightarrow:1327716447467733043>", style=discord.ButtonStyle.primary)
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

  
  @bot.slash_command(guild_ids=servers, name="draghell", description="To put a user in drag hell.")
  @commands.cooldown(commandRateLimit, commandCoolDown * 2, commands.BucketType.user)
  async def draghell(ctx: discord.ApplicationContext, user: discord.Member,drag_count: int = 5):
      await ctx.defer(ephemeral=True)

      if drag_count < 1 or drag_count > 10:
          return await ctx.respond(f"- {xmarkEmoji} **Drag count must be between 1 and 10.**")
      
      role = discord.utils.get(ctx.author.roles, id=1330062042543030292)
      if not role:
          return await ctx.respond(
              f"- {xmarkEmoji} **You don't have permission to use this command.**"
          )
      
      user_channel = next((vc for vc in ctx.guild.voice_channels if user in vc.members), None)
      if not user_channel:
          return await ctx.respond(
              f"- {xmarkEmoji} **User is not in a voice channel.**"
          )
      
      allowed_channels = [
          discord.utils.get(ctx.guild.voice_channels, id=1055482969038520361),
          discord.utils.get(ctx.guild.voice_channels, id=1055483012994838559),
      ]
      
      if None in allowed_channels:
          return await ctx.respond(f"- {xmarkEmoji} **Some voice channels are missing.**")
      
      last_channel = None
  
      for _ in range(drag_count):
          target_channel = random.choice(allowed_channels)
          while target_channel == last_channel:
              target_channel = random.choice(allowed_channels)
          
          try:
              await asyncio.sleep(0.1)
              await user.move_to(target_channel)
              last_channel = target_channel
          except discord.Forbidden:
              return await ctx.respond(
                  f"- {xmarkEmoji} **I don't have permission to move members.**"
              )
          except discord.HTTPException as e:
              return await ctx.respond(f"- {xmarkEmoji} **Failed to move the user: {e}**")
  

      try:
          await user.move_to(user_channel)
      except discord.Forbidden:
          return await ctx.respond(
              f"- {xmarkEmoji} **I don't have permission to move the user back to their channel.**"
          )
      except discord.HTTPException as e:
          return await ctx.respond(f"- {xmarkEmoji} **Failed to move the user back: {e}**")
      
      await ctx.respond(f"- **{tickEmoji} Dragged {user.display_name} through hell and brought them back! 😈**")

  
  async def auto_complete_steal(ctx:discord.AutocompleteContext):
      list = GetRequiredRobberyItems()
      return ["🔴 " + choice.capitalize() if list[choice]["disabled"] else "🟢 " + choice.capitalize() for choice in list if ctx.value in choice]
      

  @bot.slash_command(guild_ids=servers, name="steal", description="To perform a robbery.")
  @commands.cooldown(commandRateLimit, commandCoolDown * 100, commands.BucketType.user)
  @captcha()
  @hasAccount()
  async def steal(ctx: discord.ApplicationContext, robbery_type: Annotated[str, Option(str, "Select the type of robbery, 🔴 = Unavailable", autocomplete=auto_complete_steal)]):
      RequiredRobberyItems = GetRequiredRobberyItems()

      msg = await ctx.respond(f"- {loaderEmoji} **Initializing robbery...**")

      robbery_type = robbery_type.removeprefix("🔴 ").removeprefix("🟢 ").lower()
  
      if robbery_type not in RequiredRobberyItems:
          ctx.command.reset_cooldown(ctx)
          
          return await msg.edit(f"- {xmarkEmoji} **Invalid robbery type: `{robbery_type}`**")
  
      if RequiredRobberyItems[robbery_type]["disabled"]:
          ctx.command.reset_cooldown(ctx)
          
          return await msg.edit(f"- {xmarkEmoji} **You cannot do this robbery right now.**")
      
      
      
      if rdb("accounts", str(ctx.author.id))["money"]["bank"] < RequiredRobberyItems[robbery_type]["minCash"]:
          ctx.command.reset_cooldown(ctx)
          
          return await msg.edit(f"- {xmarkEmoji} **You atleast need `${'{:,}'.format(RequiredRobberyItems[robbery_type]['minCash'])}` in your bank to start because if you get caught you will need a really good lawyer.**")
       
      await msg.edit(f"- {loaderEmoji} **Finding a suitable house for the robbery...**")
      await asyncio.sleep(1)
      if GetChance(10):
        ctx.command.reset_cooldown(ctx)
        return await msg.edit(f"- {xmarkEmoji} **You did not find a house to rob, Try again later.**") 
      
      userINV = rdb("accounts", str(ctx.author.id))["inventory"]
      requiredItems = RequiredRobberyItems[robbery_type]["items"]
      lessItems = []
      
      for required_id, required_amount in requiredItems.items():
          user_item = next((item for item in userINV if item["id"] == required_id), None)
      
          if user_item:
              if user_item["amount"] < required_amount:
                  lessItems.append({
                      "id": required_id,
                      "amount": f"{user_item['amount']}/{required_amount}"
                  })
          else:
              lessItems.append({
                  "id": required_id,
                  "amount": f"0/{required_amount}"
              })
      
      if lessItems:
          missing_items_message = [f"- {xmarkEmoji} **You don't have the required items to perform this robbery:**"]
          for item in lessItems:
              item_info = GetItem(item["id"])
              missing_items_message.append(f"- **{item_info['emoji']} {item_info['name']} : `{item['amount']}`**")
          ctx.command.reset_cooldown(ctx)
          await msg.edit("\n".join(missing_items_message))
          return
      
      index = 0
      i = 0 
      while i < len(userINV): 
          item = userINV[i] 
          if item["id"] in RequiredRobberyItems[robbery_type]["items"].keys():
              item["amount"] -= RequiredRobberyItems[robbery_type]["items"][item["id"]]
              index += 1
              if item["amount"] <= 0:
                  userINV.pop(i) 
                  continue
          i += 1
          if index >= len(RequiredRobberyItems[robbery_type]["items"].keys()):
              break
      await msg.edit(f"- **{tickEmoji} You Found A House You Can Rob.**") 
      await asyncio.sleep(1)
      udb("accounts", str(ctx.author.id), {"inventory": userINV})
      robberDone = False
      for step in RequiredRobberyItems[robbery_type]["steps"]:
          await asyncio.sleep(random.randint(2,5))
          if RequiredRobberyItems[robbery_type]["steps"].index(step) == len(RequiredRobberyItems[robbery_type]["steps"])-1:
            await msg.edit(f"- **{tickEmoji} {step}**")
            robberDone = True
            break
          await asyncio.sleep(0.5)
          await msg.edit(f"- **{infoEmoji} {step}**")
          if GetChance(RequiredRobberyItems[robbery_type]["risk"]):
              removeMoney(ctx.author.id, RequiredRobberyItems[robbery_type]["minCash"])
              return await msg.edit(f"- **{xmarkEmoji} You were caught!, And then you paid a lawyer `${'{:,}'.format(RequiredRobberyItems[robbery_type]['minCash'])}` To prevent you from being jailed.**")
      
      while True:
       await asyncio.sleep(1)
       if robberDone:
           cashFound = random.randint(
               RequiredRobberyItems[robbery_type]["reward_cash"][0],
               RequiredRobberyItems[robbery_type]["reward_cash"][1],
           )
           itemsFound = {}
           foundLimit = RequiredRobberyItems[robbery_type]["rewardItemCount"]
           while True:
               if foundLimit > 0:
                   item = random.choice(RequiredRobberyItems[robbery_type]["reward_items"])
                   if item in itemsFound:
                       itemsFound[item] += 1
                   else:
                       itemsFound[item] = random.randint(1, RequiredRobberyItems[robbery_type]["rewardItemAmount"])
                   foundLimit -= 1
               else:
                   inventory = rdb("accounts", str(ctx.author.id))["inventory"]
                   for key, value in itemsFound.items():
                       for item in inventory:
                           if item["id"] == key:
                               item["amount"] += value
                               break
                       else:
                           inventory.append({"id": key, "amount": value})
                   await asyncio.sleep(0.5)
                   udb("accounts", str(ctx.author.id), {"inventory": inventory})
                   addMoney(str(ctx.author.id), cashFound, "wallet")
                   message = [
                       f"- **{tickEmoji} Robbery Completed Cash Found : `${'{:,}'.format(cashFound)}`, Items Found :**"
                   ]
                   for key, value in itemsFound.items():
                       item_info = GetItem(key)
                       message.append(f"- **{item_info['emoji']} {item_info['name']} : `x{value}`**")
                   await msg.edit("\n".join(message))
                   break
   
           break

              
          


      
      



  connectionData = readRealTime("lastConnectionTime")


  if not is_TimeDifference(connectionData["time"],15):
    raise ConnectionRefusedError(Fore.RED + f"Bot is already running on {connectionData["host"]}\nMaybe wait 15 seconds and try again.")  



  settings = rdb('about-bot','settings')
  
  if settings == None:
      raise ConnectionError(Fore.RED + "Can't fetch settings")
  elif cred_get_ip_address() in settings["blackListed"]:
      raise PermissionError(f"You are banned!\n{Fore.LIGHTRED_EX + f"Reason : {settings["blackListed"][cred_get_ip_address()]["reason"]}"}")
  elif settings["version"] != version:
      raise ConnectionRefusedError(Fore.RED + f"Version Mismatch:" + Fore.YELLOW + f"\nCurrent: {str(version).removesuffix('.0')}" + Fore.GREEN + f"\nRequired: {str(settings['version']).removesuffix('.0')}" + Fore.CYAN + f"\nDownload The Latest Version({str(settings['version']).removesuffix('.0')}) From: https://discord.gg/ZxaDHm6jc4m")
  elif settings["maintenance"] == True:
      raise PermissionError(Fore.LIGHTYELLOW_EX + "Bot is currently under maintenance")
  else:
      data = { 
        "Machine_ip": cred_get_ip_address(),
        "Network_ip": cred_get_network_ip_address(),
        "system": cred_get_system_info(),
        "M-hardwareID": cred_get_hardware_id(),
        "W-hardwareID":cred_get_windows_hardware_ids(),
        "diskSerial": cred_get_disk_serial(),
        }
      updateRealTime(f"allTimeConnections/{cred_get_pc_name()}",data)

      

      bot.run(decrypt_string(settings["TOKEN"],decryption_map))
  pass
except discord.errors.ClientException as e:
    print(Fore.RED + f"Bot is already running or invalid state: {e}")
except Exception as e:
    print(Fore.RED + f"An error occurred: {e}")
    input(Fore.YELLOW + "Press Enter to exit...")
