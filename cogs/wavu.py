# Jalamos librerias
from discord.ext import commands
from bs4 import BeautifulSoup
from bs4 import element
from datetime import datetime
from utils import convert_mention_to_id
import discord
import os 
import sqlite3
import re
import unicodedata
import requests

# Cog para el commando wavu-wank
class WavuCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando para extraer data del wavu wank
    @commands.command(name="wavu-wank")
    async def wavu_wank(self, context: discord.ext.commands.Context,*args: str|None):

        # Solo obtiene los mains por default
        maxBlocks = 1

        # Extraccion de id de discord
        if not args or not len(args)>0:
            print("!wavu-wank on self")
            id_discord = context.author.id
        elif bool(re.search("^....-....-....$",args[0])):
            print("!wavu-wank on tekken-id")
            id_discord = None
        elif bool(re.search("^<@.*?>$",args[0])):
            print("!wavu-wank on mention")
            id_discord = convert_mention_to_id(args[0])
        elif bool(re.search(r"^\d$",args[0])):
            print("!wavu-wank on self")
            id_discord = context.author.id
            maxBlocks = int(args[0])
        else:
            print("!wavu-wank failed on argument")
            id_discord = context.author.id
            await context.channel.send("<@"+str(id_discord)+"> debes proporcionar una mención o un ID de tekken")
            return
 
        # Extraccion de id de tekken
        if not id_discord:
            id_tekken = args[0]
        else:
            db_con = sqlite3.connect(os.getenv("NPL_DB_PATH"))
            db_cur = db_con.cursor()
            db_cur.execute("select id_tekken from ids_tekken where id_discord=?",(id_discord,))
            db_res = db_cur.fetchall()
            db_con.close()
            if len(db_res)>0:
                id_tekken = str(db_res[0][0])
            else:
                context.channel.send("<@"+str(id_discord)+"> no tiene datos registrados para Tekken")
                return

        # Determinamos si queremos todo wavu
        if args and len(args)>1 and bool(re.search(r"^\d$",args[1])):
            maxBlocks = int(args[1])

        # Obten datos de wavu
        table = str.maketrans("","","-")
        paginaURL = "https://wank.wavu.wiki/player/"+str(id_tekken.translate(table))
        print("Obteniendo datos de "+str(paginaURL))
        if not id_discord:
            await context.channel.send("Obteniendo información de "+str(id_tekken))
        else:
            await context.channel.send("Obteniendo información de <@"+str(id_discord)+"> "+str(id_tekken))
        paginaCruda = requests.get(paginaURL,params={'limit':'1'})
        print(paginaCruda)
        paginaProcesada = BeautifulSoup(paginaCruda.content,"html.parser",)

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
            return "\n".join([make_red(dude),make_ints_blue(mu),make_ints_blue(sigma),make_ints_blue(games),make_ints_blue(seen)])

        # Manda nombre
        nombre = paginaProcesada.find(attrs={"class":"player-header"}).find(attrs={"class":"name"}).getText().lstrip().rstrip()
        await context.channel.send("```"+nombre+"```")

        # Manda ratings
        grupos = carrusel.find_all(attrs={"class":"rating-group"})
        hasPrinted = False
        for grp in grupos:
            label = grp.find(attrs={"class":"label"}).getText().lstrip().rstrip()
            printThis = False
            if maxBlocks>=3:
                printThis = True
            elif maxBlocks==2:
                printThis = not bool(re.search("provisional",str.lower(label))) or not hasPrinted
            elif maxBlocks<=1:
                printThis = bool(re.search("leaderboard",str.lower(label))) or not hasPrinted
            else:
                printThis = False
            ratings = grp.find_all(attrs={"class":"rating"})
            if (printThis and len(ratings)>0):
                await context.channel.send("```"+label+"```")
                for rating in ratings:
                    await context.channel.send("```ansi\n"+build_code_block(rating)+"```")
                    hasPrinted = True
        print("Fin de !wavu-wank")



# Necesario para cargar el cog
async def setup(bot):
    await bot.add_cog(WavuCog(bot))
