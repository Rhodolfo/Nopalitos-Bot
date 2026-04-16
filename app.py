# Jalamos librerias
from discord.ext import commands
from utils import remove_accents
import discord
import os 

# Declaramos constantes
bot_token = os.getenv('NPL_TOKEN')

# Variables internas del bot
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix="!",intents=intents)
bot.vars = {}

# Dias de la semana y roles de bloqueo
bot.vars["max_retas_dia"] = 3
bot.vars["days_hr"] = ['Lunes','Martes','Miércoles','Jueves','Viernes']
bot.vars["blocks"] = [
    ("ocupado-lunes","Duelo Confirmado Lunes"),
    ("ocupado-martes","Duelo Confirmado Martes"),
    ("ocupado-miercoles","Duelo Confirmado Miercoles"),
    ("ocupado-jueves","Duelo Confirmado Jueves"),
    ("ocupado-viernes","Duelo Confirmado Viernes")
]

# Dias de la semana en formato ASCIII
bot.vars["days_ascii"] = [str.lower(remove_accents(ss)) for ss in bot.vars["days_hr"]]

# Este evento se detona cuando el bot se prende inicialmente
@bot.event
async def on_ready():
    print("Nopalibot has logged in")
    cogs = ["cogs.reactions","cogs.tekken_id","cogs.ft","cogs.ft_force","cogs.calendario","cogs.wavu"]
    for cog in cogs:
        print("Loading "+cog)
        await bot.load_extension(cog)
    print("Finished loading cogs")

# Corre el bot
bot.run(bot_token)
