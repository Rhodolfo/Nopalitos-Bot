# Jalamos librerias
from discord.ext import commands
from datetime import datetime
import discord
import os 
import sqlite3
import re


# Cog para el commando tekken-id
class CalendarioCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando para desplegar todos los duelos
    @commands.command(name="calendario")
    async def calendario(self,context: discord.ext.commands.Context):
        curday = datetime.now().weekday()
        db_con = sqlite3.connect(os.getenv("NPL_DB_PATH"))
        db_cur = db_con.cursor()
        query = "select id_dia from (select distinct id_dia as id_dia from duelos) order by iif(id_dia<"+str(curday)+",10+id_dia,id_dia)"
        db_cur.execute(query)
        db_res = [xx[0] for xx in db_cur.fetchall()]
        days_hr = self.bot.vars["days_hr"]
        if len(db_res)>0:
            cal = discord.Embed(
                type='rich',
                colour=discord.Colour.blue(),
                title="Duelos Programados"
            )
            def add_separation(thick: bool):
                if (thick):
                    cal.add_field(name="=====================",value="",inline=False)
                else:
                    cal.add_field(name="~~-------------------------~~",value="",inline=False)
                return
            add_separation(True)
            switch = False
            for id_dia in db_res:
                db_cur.execute("select id_discord_a,id_discord_b from duelos where id_dia=?",(id_dia,))
                duelos = [context.guild.get_member(int(ss[0])).display_name+" versus "+context.guild.get_member(int(ss[1])).display_name for ss in db_cur.fetchall()]
                free = self.bot.vars["max_retas_dia"] - len(duelos)
                if (free>1):
                    nameEmbed = days_hr[id_dia]+": "+str(free)+" duelos libres"
                elif (free==1):
                    nameEmbed = days_hr[id_dia]+": 1 duelo libre"
                else:
                    nameEmbed = days_hr[id_dia]+": Sin duelos libres"
                if id_dia==0 and switch:
                    add_separation(False)
                switch=True
                cal.add_field(name=nameEmbed,value="\n".join(duelos),inline=False)
            # add_separation(True)
            mention_config = {"everyone":False,"users":False}
            await context.channel.send(embed=cal,allowed_mentions=discord.AllowedMentions(**mention_config))
        else:
            await context.channel.send("No hay duelos confirmados en la base de datos.")
        


# Necesario para cargar el cog
async def setup(bot):
    await bot.add_cog(CalendarioCog(bot))
