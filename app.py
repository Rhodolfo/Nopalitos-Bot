# Jalamos librerias
from discord.ext import commands
from bs4 import BeautifulSoup
from bs4 import element
from datetime import datetime
import discord
import os 
import sqlite3
import re
import unicodedata
import requests



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
def convert_mention_to_id(mention: str):
    return int(mention[1:][:len(mention)-2].replace("@","").replace("!",""))

# Quitamos acentos
def remove_accents(input_str: str):
    # NFD decomposes characters into their base and combining marks
    nfkd_form = unicodedata.normalize('NFD', input_str)
    # Filter out characters that are "combining marks" (category 'Mn')
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

# Dias de la semana en formato ASCIII
days_ascii = [str.lower(remove_accents(ss)) for ss in days_hr]
 


# Este evento se detona cuando el bot se prende inicialmente
@bot.event
async def on_ready():
    print("Nopalibot en consola listo!")



# Este evento se detona cuando alguien reacciona a un mensaje
@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
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
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
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
async def tekken_id(context: discord.ext.commands.Context, arg: str|None):

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
@commands.has_role("Nopalote")
async def clear_all(context: discord.ext.commands.Context):
    return
    db_con = sqlite3.connect(db_pth)
    db_cur = db_con.cursor()
    channel = bot.get_channel(context.message.channel.id)
    db_cur.execute("delete from duelos")
    db_con.commit()
    db_con.close()
    await channel.send("Todas los duelos han sido eliminados.")

# Comando para desplegar todos los duelos
@bot.command(name="calendario")
async def calendario(context: discord.ext.commands.Context):
    curday = datetime.now().weekday()
    channel = bot.get_channel(context.message.channel.id)
    db_con = sqlite3.connect(db_pth)
    db_cur = db_con.cursor()
    db_cur.execute("select distinct id_dia from duelos order by iif(id_dia<"+str(curday)+",id_dia,10+id_dia)")
    db_res = [xx[0] for xx in db_cur.fetchall()]
    if len(db_res)>0:
        cal = discord.Embed(
            type='rich',
            colour=discord.Colour.blue(),
            title="Duelos Programados"
        )
        for id_dia in db_res:
            db_cur.execute("select id_discord_a,id_discord_b from duelos where id_dia=?",(id_dia,))
            duelos = [context.guild.get_member(int(ss[0])).display_name+" versus "+context.guild.get_member(int(ss[1])).display_name for ss in db_cur.fetchall()]
            cal.add_field(name=days_hr[id_dia],value="\n".join(duelos),inline=False)
        mention_config = {"everyone":False,"users":False}
        await channel.send(embed=cal,allowed_mentions=discord.AllowedMentions(**mention_config))
    else:
        await channel.send("No hay duelos confirmados en la base de datos.")
        
    



# Comando !ft, por ahora solo reacciona en el canal #tekken
@bot.command(name="ft")
async def ft(context: discord.ext.commands.Context, *args: str):

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
        async def button_accept_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            print("Aceptando duelo")
            mentions = interaction.message.mentions
            id_a = interaction.message.mentions[0].id
            id_b = interaction.message.mentions[1].id
            dx_a = interaction.message.content.find(str(id_a))
            dx_b = interaction.message.content.find(str(id_b))
            if (dx_a<dx_b):
                id_init = int(id_a)
                id_endr = int(id_b)
            else:
                id_init = int(id_b)
                id_endr = int(id_a)
            pusher = int(interaction.user.id)
            game = str(interaction.message.embeds[0].author.name)
            print("Game: "+str(game))
            print("Init: "+str(id_init))
            print("Endr: "+str(id_endr))
            print("Push: "+str(pusher))
            if (pusher==id_endr):
                db_con = sqlite3.connect(db_pth)
                db_cur = db_con.cursor()
                db_cur.execute("select id_dia,id_discord_a,id_discord_b,juego from duelos where id_dia=?",(id_dia,))
                db_res = db_cur.fetchall()
                if (len(db_res)<maxRetasDia):
                    db_cur.execute("insert into duelos values (?,?,?,?)",(id_dia,id_init,id_endr,game))
                    db_con.commit()
                    await interaction.message.delete()
                    message = "```ansi\n\u001b[0;34mTENEMOS DUELO CONFIRMADO\u001b[0m\n```\n<@"+str(id_discord_a)+"> <@"+str(id_discord_b)+"> ["+str(game)+"] "+str(days_hr[id_dia])
                    await challenge_channel.send(message)
                else:
                    await interaction.response.send_message("Este día ya tiene "+str(maxRetasDia)+" duelos o más programados.")
            else:
                return
        @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red,row=0)
        async def button_reject_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            print("Rechazando duelo")
            mentions = interaction.message.mentions
            id_a = interaction.message.mentions[0].id
            id_b = interaction.message.mentions[1].id
            dx_a = interaction.message.content.find(str(id_a))
            dx_b = interaction.message.content.find(str(id_b))
            if (dx_a<dx_b):
                id_init = int(id_a)
                id_endr = int(id_b)
            else:
                id_init = int(id_b)
                id_endr = int(id_a)
            pusher = int(interaction.user.id)
            game = str(interaction.message.embeds[0].author.name)
            print("Game: "+str(game))
            print("Init: "+str(id_init))
            print("Endr: "+str(id_endr))
            print("Push: "+str(pusher))
            if (pusher==id_endr):
                await interaction.message.delete()
            else:
                return

    # Emite el reto
    await challenge_channel.send(content=message,embed=invite,view=ChallengeView(timeout=None))



@bot.command(name="ft-force")
@commands.has_role("Nopalote")
async def ft_force(context: discord.ext.commands.Context,*args: str):

    # Declaraciones iniciales para todas las opciones
    db_con = sqlite3.connect(db_pth)
    db_cur = db_con.cursor()
    id_channel = int(context.message.channel.id)
    channel = bot.get_channel(id_channel)
    valid_channels = [int(os.environ["NPL_CNL_TEKKEN8"])]
    valid_games = ["TEKKEN 8"]
    valid_days = days_ascii

    # Terminamos este comando si no esta en un canal valido o si no retamos a alguien valido
    if (not id_channel in valid_channels):
        return
    elif not len(args)>0 or not bool(re.search("^<@.*?>$",args[0])):
        message = "Este comando requiere tres argumentos: dos menciones y un dia."
        await channel.send(message)
        return
    elif not len(args)>1 or not bool(re.search("^<@.*?>$",args[1])):
        message = "Este comando requiere tres argumentos: dos menciones y un dia."
        await channel.send(message)
        return
    elif not len(args)>2:
        message = "Este comando requiere que especifiques el día que quieres retar."
        await channel.send(message)
        return
    else:
        # El retador
        id_discord_a = convert_mention_to_id(args[0])
        # Declaramos id_discord_b ya que pasamos los checks, checamos que no sea autoreta
        id_discord_b = convert_mention_to_id(args[1])
        if id_discord_b==id_discord_a:
            message = "<@"+str(id_discord_a)+"> "+"No puedes retarte a ti mismo"
            await channel.send(message)
            return
        # Terminamos si el dia de la semana no es valido
        dia_sem = str.lower(remove_accents(args[2]))
        if not dia_sem in valid_days:
            message = "<@"+str(id_discord_a)+"> "+"Día de la semana no válido."
            await channel.send(message)
            return
        else:
            id_dia = valid_days.index(dia_sem)
        # Finalmente determinamos el juego
        id_juego = valid_channels.index(id_channel)
        nm_juego = valid_games[id_juego]

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
    maxRetasDia = 100
    class ChallengeView(discord.ui.View):
        @discord.ui.button(label="Aceptar", style=discord.ButtonStyle.green,row=0)
        async def button_accept_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            print("Aceptando duelo")
            mentions = interaction.message.mentions
            id_a = interaction.message.mentions[0].id
            id_b = interaction.message.mentions[1].id
            dx_a = interaction.message.content.find(str(id_a))
            dx_b = interaction.message.content.find(str(id_b))
            if (dx_a<dx_b):
                id_init = int(id_a)
                id_endr = int(id_b)
            else:
                id_init = int(id_b)
                id_endr = int(id_a)
            pusher = int(interaction.user.id)
            game = str(interaction.message.embeds[0].author.name)
            print("Game: "+str(game))
            print("Init: "+str(id_init))
            print("Endr: "+str(id_endr))
            print("Push: "+str(pusher))
            if (pusher==id_endr):
                db_con = sqlite3.connect(db_pth)
                db_cur = db_con.cursor()
                db_cur.execute("select id_dia,id_discord_a,id_discord_b,juego from duelos where id_dia=?",(id_dia,))
                db_res = db_cur.fetchall()
                if (len(db_res)<maxRetasDia):
                    db_cur.execute("insert into duelos values (?,?,?,?)",(id_dia,id_init,id_endr,game))
                    db_con.commit()
                    await interaction.message.delete()
                    message = "```ansi\n\u001b[0;34mTENEMOS DUELO CONFIRMADO\u001b[0m\n```\n<@"+str(id_discord_a)+"> <@"+str(id_discord_b)+"> ["+str(game)+"] "+str(days_hr[id_dia])
                    await challenge_channel.send(message)
                else:
                    await interaction.response.send_message("Este día ya tiene "+str(maxRetasDia)+" duelos o más programados.")
            else:
                return
        @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red,row=0)
        async def button_reject_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            print("Rechazando duelo")
            mentions = interaction.message.mentions
            id_a = interaction.message.mentions[0].id
            id_b = interaction.message.mentions[1].id
            dx_a = interaction.message.content.find(str(id_a))
            dx_b = interaction.message.content.find(str(id_b))
            if (dx_a<dx_b):
                id_init = int(id_a)
                id_endr = int(id_b)
            else:
                id_init = int(id_b)
                id_endr = int(id_a)
            pusher = int(interaction.user.id)
            game = str(interaction.message.embeds[0].author.name)
            print("Game: "+str(game))
            print("Init: "+str(id_init))
            print("Endr: "+str(id_endr))
            print("Push: "+str(pusher))
            if (pusher==id_endr):
                await interaction.message.delete()
            else:
                return

    # Emite el reto
    await challenge_channel.send(content=message,embed=invite,view=ChallengeView(timeout=None))



# Comando para extraer data del wavy wank
@bot.command(name="wavu-wank")
async def wavu_wank(context: discord.ext.commands.Context,arg: str|None):

    # Extraccion de id de tekken
    print("!wavu-wank")
    id_tekken = "2QH3fjmFbrtd"

    # Obten datos de wavu
    paginaURL = "https://wank.wavu.wiki/player/"+str(id_tekken)
    print("Obteniendo datos de "+str(paginaURL))
    xx = context.channel.send("Obteniendo información de PLACEHOLDER PLACEHOLDER")
    await xx
    paginaCruda = requests.get(paginaURL)
    paginaProcesada = BeautifulSoup(paginaCruda.text,"html.parser")

    # Jala el carrusel de rankings
    carrusel = paginaProcesada.find(attrs={"class":"player-ratings"})
    if not carrusel:
        print("Datos de wavu han fallado al buscar el carrusel")
        return

    # Crea bloque de codigo para el rating de un solo personaje en Wavu
    def build_code_block(rating: element.Tag):
        def make_blue(ss: str):
            return "\u001b[0;34m"+ss+"\u001b[0m"
        def make_red(ss: str):
            return "\u001b[0;31m"+ss+"\u001b[0m"
        def make_ints_blue(ss: str):
            return " ".join([make_blue(xx) if re.search(r"^\d",xx) else xx for xx in ss.split()])
        dude = rating.find(attrs={"class":"char"}).getText().lstrip().rstrip()
        mu = rating.find(attrs={"class":"mu"}).getText().lstrip().rstrip()
        sigma = rating.find(attrs={"class":"sigma"}).getText().lstrip().rstrip()
        games = rating.find(attrs={"class":"games"}).getText().lstrip().rstrip()
        seen = rating.find(attrs={"class":"last-seen"}).getText().lstrip().rstrip()
        return "```ansi\n"+("\n".join([make_red(dude),make_ints_blue(mu),make_ints_blue(sigma),make_ints_blue(games),make_ints_blue(seen)]))+"```"

    # Manda nombre
    nombre = paginaProcesada.find(attrs={"class":"player-header"}).find(attrs={"class":"name"}).getText().lstrip().rstrip()
    await context.channel.send("```"+nombre+"```")

    # Manda ratings
    grupos = carrusel.find_all(attrs={"class":"rating-group"})
    for grp in grupos:
        label = grp.find(attrs={"class":"label"}).getText().lstrip().rstrip()
        ss = " ".join([build_code_block(ss) for ss in grp.find_all(attrs={"class":"rating"})])
        await context.channel.send("```"+label+"``` "+ss)



bot.run(bot_token)
