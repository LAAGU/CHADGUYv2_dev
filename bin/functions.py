import string
import random
import math


def MergeDictArray(given_list, main_list):
    main_dict = {item['id']: item for item in main_list}

    for item in given_list:
        item_id = item['id']
        item_amount = item['amount']

        if item_id in main_dict:
            main_dict[item_id]['amount'] += item_amount

            if main_dict[item_id]['amount'] <= 0:
                del main_dict[item_id]
        else:
            if item_amount > 0:
                main_dict[item_id] = {'id': item_id, 'amount': item_amount}

    return list(main_dict.values())

def GetChance(percentage: float) -> bool:
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100 inclusive.")
    return random.uniform(0, 100) < percentage


agentArray : list[dict] = [
        {
            "name": "BRIMSTONE",
            "info": "Joining from the U.S.A., Brimstone's orbital arsenal ensures his squad always has the advantage. His ability to deliver utility precisely and safely make him the unmatched boots-on-the-ground commander.",
            "img": ["https://media.tenor.com/eHVwx0Omr4gAAAAe/brimstone-olur-gibi.png"]
        },
        {
            "name": "PHOENIX",
            "info": "Hailing from the U.K., Phoenix's star power shines through in his fighting style, igniting the battlefield with flash and flare. Whether he's got backup or not, he'll rush into a fight on his own terms.",
            "img": ["https://preview.redd.it/oz1p4voo30651.jpg?width=1080&crop=smart&auto=webp&s=8f4fbddc38a6bd456cf9c0588e8e4d23ca84ce31"]
        },
        {
            "name": "SAGE",
            "info": "The stronghold of China, Sage creates safety for herself and her team wherever she goes. Able to revive fallen friends and stave off aggressive pushes, she provides a calm center to a hellish fight.",
            "img": ["https://i.pinimg.com/originals/51/d7/0e/51d70e349c658b5f4df345bad3eb7a8f.jpg"]
        },
        {
            "name": "SOVA",
            "info": "Born from the eternal winter of Russia's tundra, Sova tracks, finds, and eliminates enemies with ruthless efficiency and precision. His custom bow and incredible scouting abilities ensure that even if you run, you cannot hide.",
            "img": ["https://i.redd.it/5c2yc5s4tdu51.jpg"]
        },
        {
            "name": "VIPER",
            "info": "The American Chemist, Viper deploys an array of poisonous chemical devices to control the battlefield and choke the enemy's vision. If the toxins don't kill her prey, her mindgames surely will.",
            "img": ["https://i.redd.it/0iwtp7zqc7k61.jpg"]
        },
        {
            "name": "CYPHER",
            "info": "The Moroccan information broker, Cypher is a one-man surveillance network who keeps tabs on the enemy's every move. No secret is safe. No maneuver goes unseen. Cypher is always watching.",
            "img": ["https://pbs.twimg.com/media/GRQn774bUAAJkiZ.jpg"]
        },
        {
            "name": "REYNA",
            "info": "Forged in the heart of Mexico, Reyna dominates single combat, popping off with each kill she scores. Her capability is only limited by her raw skill, making her highly dependent on performance.",
            "img": ["https://i.redd.it/7zcxb5sxz3k61.png"]
        },
        {
            "name": "KILLJOY",
            "info": "The genius of Germany. Killjoy secures the battlefield with ease using her arsenal of inventions. If the damage from her gear doesn't stop her enemies, her robots' debuff will help make short work of them.",
            "img": ["https://i.redd.it/8kxjs0qbkxq61.jpg"]
        },
        {
            "name": "BREACH",
            "info": "Breach, the bionic Swede, fires powerful, targeted kinetic blasts to aggressively clear a path through enemy ground. The damage and disruption he inflicts ensures no fight is ever fair.",
            "img": ["https://i.ytimg.com/vi/fPItC9r0jBI/maxresdefault.jpg"]
        },
        {
            "name": "OMEN",
            "info": "A phantom of a memory, Omen hunts in the shadows. He renders enemies blind, teleports across the field, then lets paranoia take hold as his foe scrambles to learn where he might strike next.",
            "img": ["https://i.imgflip.com/7ssu6u.jpg"]
        },
        {
            "name": "JETT",
            "info": "Representing her home country of South Korea, Jett's agile and evasive fighting style lets her take risks no one else can. She runs circles around every skirmish, cutting enemies before they even know what hit them.",
            "img": ["https://pbs.twimg.com/media/FP0q76LXsAst1Hd.png"]
        },
        {
            "name": "RAZE",
            "info": "Raze explodes out of Brazil with her big personality and big guns. With her blunt-force-trauma playstyle, she excels at flushing entrenched enemies and clearing tight spaces with a generous dose of boom.",
            "img": ["https://cdnb.artstation.com/p/assets/images/images/041/482/947/large/pm_artwork-raze-final-some-blur.jpg?1631812399"]
        },
        {
            "name": "SKYE",
            "info": "Hailing from Australia, Skye and her band of beasts trail-blaze the way through hostile territory. With her creations hampering the enemy, and her power to heal others, the team is strongest and safest by Skye's side.",
            "img": ["https://embed.pixiv.net/artwork.php?illust_id=90272378&mdate=1622623933"]
        },
        {
            "name": "YORU",
            "info": "Japanese native, Yoru, rips holes straight through reality to infiltrate enemy lines unseen. Using deception and aggression in equal measure, he gets the drop on each target before they know where to look.",
            "img": ["https://i.pinimg.com/474x/80/94/fa/8094fa75e66ff5a0a4d08c3dda0ba5c9.jpg"]
        },
        {
            "name": "ASTRA",
            "info": "Ghanaian Agent Astra harnesses the energies of the cosmos to reshape battlefields to her whim. With full command of her astral form and a talent for deep strategic foresight, she's always eons ahead of her enemy's next move.",
            "img": ["https://preview.redd.it/heres-all-the-meme-face-agent-seperated-if-anyone-need-it-v0-rmmli31dt4z91.png?width=640&crop=smart&auto=webp&s=7695137c5402c8f4d7fc9743bd089a61d98577bc"]
        },
        {
            "name": "KAY/O",
            "info": "KAY/O is a machine of war built for a single purpose: neutralizing radiants. His power to Suppress enemy abilities dismantles his opponents' capacity to fight back, securing him and his allies the ultimate edge.",
            "img": ["https://pbs.twimg.com/media/E5DIm-KVUAAppDX.jpg:large"]
        },
        {
            "name": "CHAMBER",
            "info": "Well-dressed and well-armed, French weapons designer Chamber expels aggressors with deadly precision. He leverages his custom arsenal to hold the line and pick off enemies from afar, with a contingency built for every plan.",
            "img": ["https://preview.redd.it/chamber-xd-v0-vk591lzhxcz91.jpg?auto=webp&s=687e9811b055a0b235f7236d3a376e472b8b49c4"]
        },
        {
            "name": "NEON",
            "info": "Filipino Agent Neon surges forward at shocking speeds, discharging bursts of bioelectric radiance as fast as her body generates it. She races ahead to catch enemies off guard, then strikes them down quicker than lightning.",
            "img": ["https://preview.redd.it/r1zno6k150991.png?width=967&format=png&auto=webp&s=e715d1e823398c31c3b532279eab00a802b906b7"]
        },
        {
            "name": "FADE",
            "info": "Turkish bounty hunter, Fade, unleashes the power of raw nightmares to seize enemy secrets. Attuned with terror itself, she hunts targets and reveals their deepest fears—before crushing them in the dark.",
            "img": ["https://i.etsystatic.com/36567760/r/il/d2be3c/4093296249/il_570xN.4093296249_2ggw.jpg"]
        },
        {
            "name": "HARBOR",
            "info": "Hailing from India's coast, Harbor storms the field wielding ancient technology with dominion over water. He unleashes frothing rapids and crushing waves to shield his allies, or pummel those that oppose him.",
            "img": ["https://i.ytimg.com/vi/SMgmt5W8x7M/sddefault.jpg"]
        },
        {
            "name": "GEKKO",
            "info": "Gekko the Angeleno leads a tight-knit crew of calamitous creatures. His buddies bound forward, scattering enemies out of the way, with Gekko chasing them down to regroup and go again.",
            "img": ["https://i.pinimg.com/originals/c7/30/39/c730394c9596327258d188ac4028bcb0.jpg"]
        },
        {
            "name": "DEADLOCK",
            "info": "Norwegian operative Deadlock deploys an array of cutting-edge nanowire to secure the battlefield from even the most lethal assault. No one escapes her vigilant watch, nor survives her unyielding ferocity.",
            "img": ["https://us-tuna-sounds-images.voicemod.net/90dd3c57-0b1a-461b-9bc1-dfd7026dc855-1707667236048.jpg"]
        },
        {
            "name": "ISO",
            "info": "Chinese fixer for hire, Iso falls into a flow state to dismantle the opposition. Reconfiguring ambient energy into bulletproof protection, he advances with focus towards his next duel to the death.",
            "img": ["https://i.kym-cdn.com/entries/icons/facebook/000/034/017/cover2.jpg"]
        },
        {
            "name": "CLOVE",
            "info": "Scottish troublemaker Clove makes mischief for enemies in both the heat of combat and the cold of death. The young immortal keeps foes guessing, even from beyond the grave, their return to the living only ever a moment away.",
            "img": ["https://www.colorado.edu/cisc/sites/default/files/styles/focal_image_square/public/callout/original.png?h=5ec076d6&itok=eNpKS9aZ"]
        },
        {
            "name": "VYSE",
            "info": "Metallic mastermind Vyse unleashes liquid metal to isolate, trap, and disarm her enemies. Through cunning and manipulation, she forces all who oppose her to fear the battlefield itself.",
            "img": ["https://i.etsystatic.com/41390297/r/il/31c6f4/6323067765/il_570xN.6323067765_6kjw.jpg"]
        },
        {
            "name": "TEJO",
            "info": "A veteran intelligence consultant from Colombia, Tejo's ballistic guidance system pressures the enemy to relinquish their ground - or their lives. His targeted strikes keep opponents off balance and under his heel.",
            "img": ["https://y.yarn.co/4a4a2356-b326-44c2-8426-7e1146c9be3f_text.gif"]
        },
        {
            "name": "SUNG JINWOO",
            "info": "A CHAD GUY",
            "img": ["https://giffiles.alphacoders.com/222/222254.gif"]
        }
    ]

itemClasses: dict = {
    "gadget": {
        "name": "Gadget",
        "description": "Gadgets are items that are used to perform a list of actions.",
    },
    "utility": {
        "name": "Utility",
        "description": "Utilities are items that are needed to run or gather certain type of items.",
    },
    "scrap": {
         "name": "Scrap",
         "description": "Scraps are left over parts of an item."
    },
    "misc": {
        "name": "Misc",
        "description": "Miscellaneous items."
    },
    "creature": {
        "name": "Creature",
        "description": "Organisms that are Alive or used to be Alive."
    }

}

items: dict = {
        "lockpick": {
            "name": "Lockpick",
            "emoji": "<:_lockpick:1330478321657581608>",
            "price": -1,
            "class": "gadget"
        },
        "phone": {
            "name": "Phone",
            "emoji": "<:phone:1326689224749219982>",
            "price": 1000,
            "class": "gadget"
        },
        "battery": {
            "name": "Battery",
            "emoji": "<:_battery:1328863097477271602>",
            "price": 100,
            "class": "utility"
        },
        "cell": {
            "name": "Cell",
            "emoji": "<:_cell:1329292801132728330>",
            "price": 10,
            "class": "scrap"
        },
        "fishing_rod": {
            "name": "Fishing Rod",
            "emoji": "<:_fishing_rod:1329299776403017790>",
            "price": 200,
            "class": "utility"
        },
        "aura": {
            "name": "Aura",
            "emoji": "<:_aura:1329300381884354571>",
            "price": -1,
            "class": "misc"
        },
        "blue_gem": {
            "name": "Blue Gem",
            "emoji": "<a:_blue_gem:1329300836534321247>",
            "price": 2000,
            "class": "misc"
        },
        "fish_bait": {
            "name": "Fish Bait",
            "emoji": "<:_fish_bait:1329301407119052810>",
            "price": 5,
            "class": "utility"
        },
        "gold_coin": {
            "name": "Gold Coin",
            "emoji": "<:_gold_coin:1329301808123875398>",
            "price": 1500,
            "class": "misc"
        },
        "poke_coin": {
            "name": "Poke Coin",
            "emoji": "<:_poke_coin:1329302091960815646>",    
            "price": -1,
            "class": "misc"
        },
        "moon_coin": {
            "name": "Moon Coin",
            "emoji": "<:_moon_coin:1329302875448414251>",
            "price": -1,
            "class": "misc"
        },
        "star_coin": {
            "name": "Star Coin",
            "emoji": "<:_star_coin:1329302881324765184>",
            "price": -1,
            "class": "misc"
        },
        "star_fish": {
            "name": "Star Fish",
            "emoji": "<:_star_fish:1329309807928148040>",
            "price": 30,
            "class": "creature"
        },
        "alien_fish": {
            "name": "Alien Fish",
            "emoji": "<:_alien_fish:1329309976958599189>",
            "price": 70,
            "class": "creature"
        },
        "fire_crab": {
            "name": "Fire Crab",
            "emoji": "<:_fire_crab:1329310269171826764>",
            "price": 50,
            "class": "creature"
        },
        "water_crab": {
            "name": "Water Crab",
            "emoji": "<:_water_crab:1329310272414027890>",
            "price": 20,
            "class": "creature"
        },
        "blue_koi": {
            "name": "Blue Koi",
            "emoji": "<:_blue_koi:1329311301683511358>",
            "price": 15,
            "class": "creature"
        },
        "pink_koi": {
            "name": "Pink Koi",
            "emoji": "<:_pink_koi:1329311303973470208>",
            "price": 18,
            "class": "creature"
        },
        "mixed_koi": {
            "name": "Mixed Koi",
            "emoji": "<:_mixed_koi:1329311306783658025>",
            "price": 40,
            "class": "creature"
        },
        "piranha": {
            "name": "Piranha",
            "emoji": "<:_piranha:1329312096579747923>",
            "price": 60,
            "class": "creature"
        },
        "whale": {
            "name": "Whale",
            "emoji": "<:_whale:1329312333394088028>",
            "price": 100,
            "class": "creature"
        },
        "poisson_fish": {
            "name": "Poisson Fish",
            "emoji": "<:_poisson_fish:1329312543214403594>",
            "price": 80,
            "class": "creature"
        },
        "oni_fish": {
            "name": "Oni Fish",
            "emoji": "<:_oni_fish:1329312774534332487>",
            "price": 150,
            "class": "creature"
        },
        "chad_fish": {
            "name": "Chad Fish",
            "emoji": "<:_chad_fish:1329313022023438387>",
            "price": 69,
            "class": "creature"
        },
        "exotic_fish": {
            "name": "Exotic Fish",
            "emoji": "<:_exotic_fish:1329313180131790908>",
            "price": 100,
            "class": "creature"
        },
        "gold_fish": {
            "name": "Gold Fish",
            "emoji": "<:_gold_fish:1329313662250258472>",
            "price": 20,
            "class": "creature"
        },
        "blue_fish": {
            "name": "Blue Fish",
            "emoji": "<:_blue_fish:1329313872590409849>",
            "price": 15,
            "class": "creature"
        },
        "red_bass": {
            "name": "Red Bass",
            "emoji": "<:_red_bass:1329314213612617790> ",
            "price": 12,
            "class": "creature"
        },
        "green_bass": {
            "name": "Green Bass",
            "emoji": "<:_green_bass:1329314207723946116>",
            "price": 8,
            "class": "creature"
        },
        "orange_bass": {
            "name": "Orange Bass",
            "emoji": "<:_orange_bass:1329314210932592713>",
            "price": 10,
            "class": "creature"
        },
        "crowbar": {
            "name": "Crowbar",
            "emoji": "<:_crowbar:1330463820031987816>",
            "price": 150,
            "class": "utility"
        },
        "bag": {
            "name": "Bag",
            "emoji": "<:_bag:1330464434128420927>",
            "price": 100,
            "class": "utility"
        },
        "silver_chain": {
            "name": "Silver Chain",
            "emoji": "<:_silver_chain:1330534762879778819>",
            "price": 2000,
            "class": "misc"
        },
        "diamond_ring":{
            "name": "Diamond Ring",
            "emoji": "<:_diamond_ring:1330534222741508106>",
            "price": 6000,
            "class": "misc"
        },
        "ruby_ring":{
            "name": "Ruby Ring",
            "emoji": "<:_ruby_ring:1330534228336574474>",
            "price": 3500,
            "class": "misc"
        },
        "emerald_ring":{
            "name": "Emerald Ring",
            "emoji": "<:_emerald_ring:1330534225358880838>",
            "price": 4500,
            "class": "misc"
        }

}


requiredRobberyItems : dict = {
    "house": {
        "risk": 8,
        "disabled":False,
        "minCash":1000,
        "steps":[
            "Checking if someone is near the house...",
            "Lockpicking the door...",
            "Entered The House...",
            "Finding valueable items and cash...",
            "Using crowbar to open a safe...",
            "Putting every thing in the bag...",
            "Fleeing from the area...",
            "House Robbed Successfully! Calculating Valuables..."
        ],
        "items": {
            "lockpick":3,
            "crowbar":1,
            "bag":1
        },
        "reward_cash":[500,5000],
        "reward_items":['phone','blue_gem','silver_chain','diamond_ring','ruby_ring','emerald_ring'],
        "rewardItemCount":5,
        "rewardItemAmount":2
    },
    "shop": {
        "disabled":True
    },
    "atm": {
        "disabled":True
    },
    "bank": {
        "disabled":True
    }
}


dailyRewards: list[dict] = [
    {
        "amount": [50,200,500,1000,1200,1500,2000,2500,3000,4000,5000,6000,7000,8000,9000,10000],
        "name": "money"
    }
]

craftingRecipes: dict = {
    "phone": [
        {
            "item": "battery",
            "amount": 1
        }
    ],
    "battery": [
        {
            "item": "cell",
            "amount": 3
        }
    ]
}

fishingCatchables = [
        {"id":"cell","max":5,"probibility":30},
        {"id":"gold_coin","max":2,"probibility":5},
        {"id":"star_fish","max":7,"probibility":32},
        {"id":"alien_fish","max":3,"probibility":15},
        {"id":"fire_crab","max":5,"probibility":18},
        {"id":"water_crab","max":6,"probibility":20},
        {"id":"blue_koi","max":8,"probibility":22},
        {"id":"pink_koi","max":5,"probibility":16},
        {"id":"mixed_koi","max":2,"probibility":13},
        {"id":"piranha","max":1,"probibility":8},
        {"id":"whale","max":1,"probibility":6},
        {"id":"poisson_fish","max":2,"probibility":9},
        {"id":"oni_fish","max":1,"probibility":6},
        {"id":"chad_fish","max":1,"probibility":10},
        {"id":"exotic_fish","max":1,"probibility":6},
        {"id":"gold_fish","max":2,"probibility":10},
        {"id":"red_bass","max":1,"probibility":8},
        {"id":"green_bass","max":3,"probibility":12},
        {"id":"orange_bass","max":2,"probibility":10},
]

def GetRequiredRobberyItems() -> dict:
    return requiredRobberyItems

def GetDiscount(percentage,value):
    if percentage == 0:
         return value
    discount_amount = (percentage / 100) * value
    final_value = value - discount_amount
    return math.floor(final_value)
     

def GetFishingCatchables() -> list[dict]:
    return fishingCatchables

def GetRandomString(length,upperCase=False):
                letters = string.ascii_letters + string.digits
                return ''.join(random.choice(letters) for _ in range(length)) if not upperCase else ''.join(random.choice(letters) for _ in range(length)).upper()
def GetRandomNumber(length):
    numbers = string.digits
    return ''.join(random.choice(numbers) for _ in range(length)) 

def GetCraftingRecipes() -> dict:
    return craftingRecipes

def GetItemClasses() -> list[dict]:
    return itemClasses

def GetItemClass(id : str) -> dict:
    for itemClass in itemClasses:
        if itemClass.keys()[0] == id:
            return itemClass
    else:
        return {"name": "Unknown", "description": "Unknown"}

def GetRewards() -> list[dict]:
    return dailyRewards

def GetItem(id : str) -> dict:
    if id in items:
        return items[id]
    else:
        return {"name": "Unknown", "emoji": "<:unknownItem:1327725424226074624>", "price": 0}

def GetItems() -> dict:
    return items

def GetTradableItems() -> dict:
    data = {}
    for item in items:
        if items[item]["price"] != -1:
            data[item] = items[item]

    return data


def GetAgent(index : int) -> dict:
    return agentArray[index]

def GetAgentList() -> list[dict]:
    return agentArray


def create_mapping():
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:'\",.<>?/ \\"
    replacements = [
        "😀", "😁", "😂", "😃", "😄", "😅", "😆", "😇", "😈", "😉", "😊", "😋", "😌", "😍", "😎", "😏",
        "😐", "😑", "😒", "😓", "😔", "😕", "😖", "😗", "😘", "😙", "😚", "😛", "😜", "😝", "😞", "😟",
        "😠", "😡", "😢", "😣", "😤", "😥", "😦", "😧", "😨", "😩", "😪", "😫", "😬", "😭", "😮", "😯",
        "😰", "😱", "😲", "😳", "😴", "😵", "😶", "😷", "😸", "😹", "😺", "😻", "😼", "😽", "😾", "😿",
        "🚀", "🍎", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🍒", "🍍", "🥝", "🥥", "🥑", "🥒", "🥦", "🥩",
        "🍔", "🍟", "🍕", "🌭", "🍿", "🥗", "🥘", "🥙", "🥪", "🥣", "🥡", "🥢", "☕",
    ]

    assert len(characters) == len(replacements), "Character and replacement lengths must match."

    encryption_map = dict(zip(characters, replacements))
    decryption_map = {v: k for k, v in encryption_map.items()}

    return encryption_map, decryption_map

def encrypt_string(token, encryption_map):
    encrypted = ''.join(encryption_map.get(char, char) for char in token)
    return encrypted

def decrypt_string(encrypted_token, decryption_map):
    decrypted = ''.join(decryption_map.get(char, char) for char in encrypted_token)
    return decrypted

