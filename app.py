# Jalamos librerias
from discord.ext import commands
import discord
import os 
import sqlite3
import re
import unicodedata



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

# Dias de la semana
days_hr = ['Lunes','Martes','Miércoles','Jueves','Viernes']
blocks = [
    ("ocupado-lunes","Duelo Confirmado Lunes"),
    ("ocupado-martes","Duelo Confirmado Martes"),
    ("ocupado-miercoles","Duelo Confirmado Miercoles"),
    ("ocupado-jueves","Duelo Confirmado Jueves"),
    ("ocupado-viernes","Duelo Confirmado Viernes")
]



# Extrae discord id de usuario directamente de un mention
def convert_mention_to_id(mention):
    return int(mention[1:][:len(mention)-2].replace("@","").replace("!",""))

# Quitamos acentos
def remove_accents(input_str):
    # NFD decomposes characters into their base and combining marks
    nfkd_form = unicodedata.normalize('NFD', input_str)
    # Filter out characters that are "combining marks" (category 'Mn')
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])
days_ascii = [str.lower(remove_accents(ss)) for ss in days_hr]
 


# Este evento se detona cuando el bot se prende inicialmente
@bot.event
async def on_ready():
    print("Nopalibot en consola listo!")
    pass



# Este evento se detona cuando alguien reacciona a un mensaje
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



# Este evento se detona cuando alguien quita una reaccion a un mensaje
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



# Comando !tekken-id
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
        db_con.close()
    else:
        db_res = []
        db_con.close()

    # Finalmente manda un mensaje confirmando el tekken id
    if (len(db_res)>0):
        message = "<@"+str(id_discord)+">: "+db_res[0][0]
        if (mode=="register"):
            message = message + " como nuevo registro"
        await channel.send(message)
    else:
        message = "<@"+str(id_discord)+"> no tiene datos registrados para Tekken"
        await channel.send(message)



# Comando !ft, por ahora solo reacciona en el canal #tekken
@bot.command(name="ft")
async def ft(context, *args):

    # Declaraciones iniciales para todas las opciones
    db_con = sqlite3.connect(db_pth)
    db_cur = db_con.cursor()
    id_channel = int(context.message.channel.id)
    channel = bot.get_channel(id_channel)
    id_discord_a = int(context.author.id)
    valid_channels = [int(os.environ["NPL_CNL_TEKKEN8"])]
    valid_days = days_ascii
    print(args)

    # Terminamos este comando si no esta en un canal valido o si no retamos a alguien valido
    if (not id_channel in valid_channels):
        message = "<@"+str(id_discord_a)+"> "+"Este comando está bajo construcción."
        await channel.send(message)
        return
    elif not len(args)>0 or not bool(re.search("^<@.*?>$",args[0])):
        message = "<@"+str(id_discord_a)+"> "+"Este comando requiere que retes a otra persona con una mención."
        await channel.send(message)
        return
    elif not len(args)>1:
        message = "<@"+str(id_discord_a)+"> "+"Este comando requiere que especifiques el día que quieres retar."
        await channel.send(message)
        return
    else:
        # Declaramos id_discord_b ya que pasamos los checks, checamos que no sea autoreta
        id_discord_b = convert_mention_to_id(args[0])
        if id_discord_b==id_discord_a:
            message = "<@"+str(id_discord_a)+"> "+"No puedes retarte a ti mismo"
            await channel.send(message)
            return
        # Terminamos si el dia de la semana no es valido
        dia_sem = str.lower(remove_accents(args[1]))
        if not dia_sem in valid_days:
            message = "<@"+str(id_discord_a)+"> "+"Día de la semana no válido."
            await channel.send(message)
            return
        else:
            id_dia = valid_days.index(dia_sem)

    # Revisamos que no tengas reta ese dia
    db_cur.execute("select id_dia,juego from retas where id_dia=? and (id_discord_a=? or id_discord_b=?)",(id_dia,id_discord_a,id_discord_a))
    db_res = db_cur.fetchall()
    if (len(db_res)>0):
        message = "<@"+str(id_discord_a)+"> "+"Ya tienes una reta ese día."
        await channel.send(message)
        return
 
    # Revisamos que tu oponente
    db_cur.execute("select id_dia,juego from retas where id_dia=? and (id_discord_a=? or id_discord_b=?)",(id_dia,id_discord_b,id_discord_b))
    db_res = db_cur.fetchall()
    if (len(db_res)>0):
        message = "<@"+str(id_discord_a)+"> "+"Tu oponente <@"+id_discord_b+"> ya tiene una reta ese día."
        await channel.send(message)
        return

    # Vamos a revisar que el retado no tenga dias bloqueados
    current_blocks = blocks[id_dia]
    member = context.guild.get_member(id_discord_b)
    for ele in current_blocks:
        role = discord.utils.get(context.guild.roles,name=ele)
        print(role)
        print(member.roles)
        if role in member.roles:
            print(role)
            message = "<@"+str(id_discord_a)+"> "+"Tu oponente <@"+str(id_discord_b)+"> tiene un rol que bloquea ese día."
            await channel.send(message)
            return

    # Emite el reto
    challenge_channel = bot.get_channel(int(os.environ['NPL_CNL_CHALLENGE']))
    message =  "<@"+str(id_discord_a)+"> "+"ha retado a un FT a <@"+str(id_discord_b)+"> para el día "+str.lower(days_hr[id_dia])
    await challenge_channel.send(message)








    # Creamos el mensaje en el canal de confirmacion
    conf_channel = int(os.environ["NPL_CNL_CHALLENGE"])

    print(message)










    





bot.run(bot_token)

