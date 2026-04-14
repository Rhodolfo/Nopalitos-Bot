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
    id_emoji = None if not payload.emoji.id else int(payload.emoji.id)
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
    elif (int(payload.channel_id)==int(os.environ["NPL_CNL_CHALLENGE"])):
        # Esta reaccion borra duelos en el canal de duelos-confirmados
        user = await guild.fetch_member(id_user)
        role = discord.utils.get(guild.roles,name="Nopalote")
        if (role in user.roles and payload.emoji.name=='\u2705'):
            message_ob = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            if not "TENEMOS DUELO CONFIRMADO" in message_ob.content:
                return
            if not len(message_ob.mentions)==2:
                return
            id_discord_a = int(message_ob.mentions[0].id)
            id_discord_b = int(message_ob.mentions[1].id)
            last_word = str.lower(remove_accents(message_ob.content.split()[-1]))
            if not last_word in days_ascii:
                return
            id_dia = days_ascii.index(last_word)
            db_con = sqlite3.connect(db_pth)
            db_cur = db_con.cursor()
            db_cur.execute("delete from duelos where id_dia=? and ((id_discord_a=? and id_discord_b=?) or (id_discord_a=? and id_discord_b=?))",(id_dia,id_discord_a,id_discord_b,id_discord_b,id_discord_a))
            db_con.commit()
            db_con.close()
            await message_ob.delete()



# Este evento se detona cuando alguien quita una reaccion a un mensaje
@bot.event
async def on_raw_reaction_remove(payload):
    id_user = int(payload.user_id)
    id_message = int(payload.message_id)
    id_emoji = None if not payload.emoji.id else int(payload.emoji.id)
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



# Comando para matar todos los duelos
@bot.command(name="clear-all")
async def clear_all(context):
    db_con = sqlite3.connect(db_pth)
    db_cur = db_con.cursor()
    channel = bot.get_channel(context.message.channel.id)
    db_cur.execute("delete from duelos")
    db_con.commit()
    db_con.close()
    await channel.send("Todas los duelos han sido eliminados.")

# Comando para desplegar todos los duelos
@bot.command(name="calendario")
async def calendario(context):
    channel = bot.get_channel(context.message.channel.id)
    db_con = sqlite3.connect(db_pth)
    db_cur = db_con.cursor()
    db_cur.execute("select distinct id_dia from duelos order by id_dia")
    db_res = [xx[0] for xx in db_cur.fetchall()]
    if len(db_res)>0:
        cal = discord.Embed(
            type='rich',
            colour=discord.Colour.blue(),
            title="Duelos Programados"
        )
        for id_dia in db_res:
            db_cur.execute("select id_discord_a,id_discord_b from duelos where id_dia=?",(id_dia,))
            duelos = ["<@"+str(ss[0])+"> versus <@"+str(ss[1])+">" for ss in db_cur.fetchall()]
            cal.add_field(name=days_hr[id_dia],value="\n".join(duelos),inline=False)
        mention_config = {"everyone":False,"users":False}
        await channel.send(embed=cal,allowed_mentions=discord.AllowedMentions(**mention_config))
    else:
        await channel.send("No hay duelos confirmados en la base de datos.")
        
    



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
    valid_games = ["TEKKEN 8"]
    valid_days = days_ascii

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
        # Finalmente determinamos el juego
        id_juego = valid_channels.index(id_channel)
        nm_juego = valid_games[id_juego]

    # Revisamos que no tengas reta ese dia
    db_cur.execute("select id_dia,juego from duelos where id_dia=? and (id_discord_a=? or id_discord_b=?)",(id_dia,id_discord_a,id_discord_a))
    db_res = db_cur.fetchall()
    if (len(db_res)>0):
        message = "<@"+str(id_discord_a)+"> "+"Ya tienes una reta ese día."
        await channel.send(message)
        return
 
    # Revisamos que tu oponente
    db_cur.execute("select id_dia,juego from duelos where id_dia=? and (id_discord_a=? or id_discord_b=?)",(id_dia,id_discord_b,id_discord_b))
    db_res = db_cur.fetchall()
    db_con.close()
    if (len(db_res)>0):
        message = "<@"+str(id_discord_a)+"> "+"Tu oponente <@"+id_discord_b+"> ya tiene una reta ese día."
        await channel.send(message)
        return

    # Vamos a revisar que el retado no tenga dias bloqueados
    current_blocks = blocks[id_dia]
    member = context.guild.get_member(id_discord_b)
    for ele in current_blocks:
        role = discord.utils.get(context.guild.roles,name=ele)
        if role in member.roles:
            message = "<@"+str(id_discord_a)+"> "+"Tu oponente <@"+str(id_discord_b)+"> tiene un rol que bloquea ese día."
            await channel.send(message)
            return

    # Construccion del mensaje de reto
    challenge_channel = bot.get_channel(int(os.environ['NPL_CNL_CHALLENGE']))
    message =  "<@"+str(id_discord_a)+"> "+"ha retado a un FT a <@"+str(id_discord_b)+">"
    invite = discord.Embed(
        type='rich',
        colour=discord.Colour.blue(),
        title="DUELO PARA EL DÍA "+str.upper(days_hr[id_dia]),
        description="¿Aceptas el reto, <@"+str(id_discord_b)+">?"
    )
    invite.set_image(url=str(os.environ["NPL_IMG_CHALLENGE"]))
    invite.set_thumbnail(url=str(os.environ["NPL_IMG_CHALLTHMB"]))
    invite.set_author(name=nm_juego)

    # Botones de reto
    maxRetasDia = 3
    class ChallengeView(discord.ui.View):
        @discord.ui.button(label="Aceptar", style=discord.ButtonStyle.green,row=0)
        async def button_accept_callback(self, interaction, button):
            print("Aceptando, pusher vs retado")
            mentions = interaction.message.mentions()
            pusher = int(interaction.user.id)
            print(mentions)
            print(pusher)
            print(id_discord_b)
            if (pusher==id_discord_b):
                db_con = sqlite3.connect(db_pth)
                db_cur = db_con.cursor()
                db_cur.execute("select id_dia,id_discord_a,id_discord_b,juego from duelos where id_dia=?",(id_dia,))
                db_res = db_cur.fetchall()
                if (len(db_res)<maxRetasDia):
                    db_cur.execute("insert into duelos values (?,?,?,?)",(id_dia,id_discord_a,id_discord_b,nm_juego))
                    db_con.commit()
                    await interaction.message.delete()
                    message = "```ansi\n\u001b[0;34mTENEMOS DUELO CONFIRMADO\u001b[0m\n```\n<@"+str(id_discord_a)+"> <@"+str(id_discord_b)+"> ["+str(nm_juego)+"] "+str(days_hr[id_dia])
                    await challenge_channel.send(message)
                else:
                    await interaction.response.send_message("Este día ya tiene "+str(maxRetasDia)+" duelos o más programados.")
            else:
                return
        @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red,row=0)
        async def button_reject_callback(self, interaction, button):
            print("Rechazando, pusher vs retado")
            pusher = int(interaction.user.id)
            print(pusher)
            print(id_discord_b)
            if (pusher==id_discord_b):
                await interaction.message.delete()
            else:
                return

    # Emite el reto
    await challenge_channel.send(content=message,embed=invite,view=ChallengeView())










bot.run(bot_token)

