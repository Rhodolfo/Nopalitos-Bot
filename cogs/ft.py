# Jalamos librerias
from discord.ext import commands
from utils import convert_mention_to_id,remove_accents
import discord
import os 
import sqlite3
import re
import unicodedata

# Cog para el commando ft
class FtCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando ft
    @commands.command(name="ft")
    async def ft(self, context: discord.ext.commands.Context, *args: str):

        # Declaraciones iniciales para todas las opciones
        db_con = sqlite3.connect(os.getenv("NPL_DB_PATH"))
        db_cur = db_con.cursor()
        id_channel = int(context.message.channel.id)
        id_discord_a = int(context.author.id)
        valid_channels = [int(os.environ["NPL_CNL_TEKKEN8"])]
        valid_games = ["TEKKEN 8"]
        valid_days = self.bot.vars["days_ascii"]
        days_hr = self.bot.vars["days_hr"]
        maxRetasDia = self.bot.vars["max_retas_dia"]

        # Terminamos este comando si no esta en un canal valido o si no retamos a alguien valido
        if (not id_channel in valid_channels):
            print("!ft llamado en canal invalido")
            return
        elif not len(args)>0 or not bool(re.search("^<@.*?>$",args[0])):
            message = "<@"+str(id_discord_a)+"> "+"Este comando requiere que retes a otra persona con una mención."
            await context.channel.send(message)
            return
        elif not len(args)>1:
            message = "<@"+str(id_discord_a)+"> "+"Este comando requiere que especifiques el día que quieres retar."
            await context.channel.send(message)
            return
        else:
            # Declaramos id_discord_b ya que pasamos los checks, checamos que no sea autoreta
            id_discord_b = convert_mention_to_id(args[0])
            if id_discord_b==id_discord_a:
                message = "<@"+str(id_discord_a)+"> "+"No puedes retarte a ti mismo"
                await context.channel.send(message)
                return
            # Terminamos si el dia de la semana no es valido
            dia_sem = str.lower(remove_accents(args[1]))
            if not dia_sem in valid_days:
                message = "<@"+str(id_discord_a)+"> "+"Día de la semana no válido."
                await context.channel.send(message)
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
            await context.channel.send(message)
            return
 
        # Revisamos que tu oponente
        db_cur.execute("select id_dia,juego from duelos where id_dia=? and (id_discord_a=? or id_discord_b=?)",(id_dia,id_discord_b,id_discord_b))
        db_res = db_cur.fetchall()
        db_con.close()
        if (len(db_res)>0):
            message = "<@"+str(id_discord_a)+"> "+"Tu oponente <@"+id_discord_b+"> ya tiene una reta ese día."
            await context.channel.send(message)
            return

        # Vamos a revisar que el retado no tenga dias bloqueados
        current_blocks = self.bot.vars["blocks"][id_dia]
        member = context.guild.get_member(id_discord_b)
        member_nopalibot = context.guild.get_member(self.bot.user.id)
        for ele in current_blocks:
            role = discord.utils.get(context.guild.roles,name=ele)
            if role in member.roles:
                message = "<@"+str(id_discord_a)+"> "+"Tu oponente <@"+str(id_discord_b)+"> tiene un rol que bloquea ese día."
                await context.channel.send(message)
                return
            if role in member_nopalibot.roles:
                message = "<@"+str(id_discord_a)+"> "+"Este día esta bloqueado para todos."
                await context.channel.send(message)
                return

         # Construccion del mensaje de reto
        challenge_channel = self.bot.get_channel(int(os.environ['NPL_CNL_CHALLENGE']))
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
                    db_con = sqlite3.connect(os.getenv("NPL_DB_PATH"))
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



# Necesario para cargar el cog
async def setup(bot):
    await bot.add_cog(FtCog(bot))
