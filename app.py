# Jalamos librerias
from discord.ext import commands
import discord
import os 
import sqlite3
import re



# Cosas de base de datos 
db_pth = "db/nopalitos.db"

# Declaramos constantes
bot_token = os.environ['NPL_TOKEN']
msg_platform = int(os.environ['NPL_MSG_PLATFORM'])
msg_game = int(os.environ['NPL_MSG_GAME'])

# Variables internas del bot
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix="!",intents=intents)



# Extrae discord id de usuario directamente de un mention
def convert_mention_to_id(mention):
    return int(mention[1:][:len(mention)-2].replace("@","").replace("!",""))



@bot.event
async def on_ready():
    print("Nopalibot en consola listo!")
    pass

@bot.event
async def on_raw_reaction_add(payload):
    id_user = int(payload.user_id)
    id_message = int(payload.message_id)
    id_emoji = int(payload.emoji.id)
    guild = bot.get_guild(payload.guild_id)
    if id_message==msg_platform:
        user = await guild.fetch_member(id_user)
        if id_emoji==int(os.environ['NPL_EMO_XBOX']):
            role = discord.utils.get(guild.roles,name="Xbox Player")
            await user.add_roles(role)
        elif id_emoji==int(os.environ['NPL_EMO_PLAYSTATION']):
            role = discord.utils.get(guild.roles,name="PS Player")
            await user.add_roles(role)
        elif id_emoji==int(os.environ['NPL_EMO_PC']):
            role = discord.utils.get(guild.roles,name="PC Player")
            await user.add_roles(role)
    elif (id_message==msg_game):
        user = await guild.fetch_member(id_user)
        if id_emoji==int(os.environ['NPL_EMO_TEKKEN8']):
            role = discord.utils.get(guild.roles,name="Tekken")
            await user.add_roles(role)
        elif id_emoji==int(os.environ['NPL_EMO_STREET6']):
            role = discord.utils.get(guild.roles,name="SF6")
            await user.add_roles(role)
        elif id_emoji==int(os.environ['NPL_EMO_2XKO']):
            role = discord.utils.get(guild.roles,name="2XKO")
            await user.add_roles(role)



@bot.event
async def on_raw_reaction_remove(payload):
    id_user = int(payload.user_id)
    id_message = int(payload.message_id)
    id_emoji = int(payload.emoji.id)
    guild = bot.get_guild(payload.guild_id)
    if id_message==msg_platform:
        user = await guild.fetch_member(id_user)
        if id_emoji==int(os.environ['NPL_EMO_XBOX']):
            role = discord.utils.get(guild.roles,name="Xbox Player")
            await user.remove_roles(role)
        elif id_emoji==int(os.environ['NPL_EMO_PLAYSTATION']):
            role = discord.utils.get(guild.roles,name="PS Player")
            await user.remove_roles(role)
        elif id_emoji==int(os.environ['NPL_EMO_PC']):
            role = discord.utils.get(guild.roles,name="PC Player")
            await user.remove_roles(role)
    elif (id_message==msg_game):
        user = await guild.fetch_member(id_user)
        if id_emoji==int(os.environ['NPL_EMO_TEKKEN8']):
            role = discord.utils.get(guild.roles,name="Tekken")
            await user.remove_roles(role)
        elif id_emoji==int(os.environ['NPL_EMO_STREET6']):
            role = discord.utils.get(guild.roles,name="SF6")
            await user.remove_roles(role)
        elif id_emoji==int(os.environ['NPL_EMO_2XKO']):
            role = discord.utils.get(guild.roles,name="2XKO")
            await user.remove_roles(role)



@bot.command(name="tekken-id")
async def tekken_id(context, arg: str|None):

    # Declaraciones iniciales para todas las opciones
    db_con = sqlite3.connect(db_pth)
    db_cur = db_con.cursor()
    channel = bot.get_channel(context.message.channel.id)

    # Primero detectemos la intencion y tomamos el id_discord de acuerdo al contexto
    if (not arg):
        mode = "self" 
        id_discord = context.author.id
    elif bool(re.search("^....-....-....$",arg)):
        mode = "register"
        id_discord = context.author.id
        db_cur.execute("delete from ids_tekken where id_discord=?",(id_discord,))
        db_con.commit()
        db_cur.execute("insert into ids_tekken values (?,?)",(id_discord,arg))
        db_con.commit()
    elif bool(re.search("^<@.*?>$",arg)):
        mode = "query"
        id_discord = convert_mention_to_id(arg)
    else:
        mode = "invalid"
        id_discord = None

    # Obten datos de Tekken ID
    if (mode!="invalid"):
        db_cur.execute("select id_tekken from ids_tekken where id_discord=?",(id_discord,))
        db_res = db_cur.fetchall()
    else:
        db_res = []

    # Finalmente manda un mensaje confirmando el tekken id
    if (len(db_res)>0):
        message = "<@"+str(id_discord)+">: "+db_res[0][0]
        if (mode=="register"):
            message = message + " como nuevo registro"
        await channel.send(message)
    else:
        message = "<@"+str(id_discord)+"> no tiene datos registrados para Tekken"
        await channel.send(message)

bot.run(bot_token)

