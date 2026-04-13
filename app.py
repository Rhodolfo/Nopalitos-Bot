# Jalamos librerias
from discord.ext import commands
import discord
import os 
import sqlite3
import re

# Cosas de base de ddatos 
db_pth = "db/nopalitos.db"

# Declaramos constantes
bot_token = os.environ['NPL_TOKEN']
msg_platform = os.environ['NPL_MSG_PLATFORM']
msg_game = os.environ['NPL_MSN_GAME']

# Variables internas del bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!",intents=intents)



# Extrae discord id de usuario directamente de un mention
def convert_mention_to_id(mention):
    return int(mention[1:][:len(mention)-2].replace("@","").replace("!",""))



@bot.event
async def on_ready():
    print("Nopalibot en consola listo!")
    pass



@bot.command(name="tekken-id")
async def tekken_id(context, arg: str|None):

    # Declaraciones iniciales para todas las opciones
    print(context.message.content)
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
    print(mode)

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

