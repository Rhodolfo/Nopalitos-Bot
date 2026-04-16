# Jalamos librerias
from discord.ext import commands
from utils import convert_mention_to_id
import discord
import os 
import sqlite3
import re

# Cog para el commando tekken-id
class TekkenIdCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando !tekken-id
    @commands.command(name="tekken-id")
    async def tekken_id(self, context: discord.ext.commands.Context, arg: str|None):

        # Declaraciones iniciales para todas las opciones
        db_con = sqlite3.connect(os.getenv("NPL_DB_PATH"))
        db_cur = db_con.cursor()

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
            await context.channel.send(message)
        else:
            message = "<@"+str(id_discord)+"> no tiene datos registrados para Tekken"
            await context.channel.send(message)



# Necesario para cargar el cog
async def setup(bot):
    await bot.add_cog(TekkenIdCog(bot))
