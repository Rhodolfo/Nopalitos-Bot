# Jalamos librerias
from discord.ext import commands
from utils import remove_accents
import discord
import os 
import sqlite3
import re

# Cog para manejar reacciones
class ReactionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Este evento se detona cuando alguien reacciona a un mensaje
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        id_user = int(payload.user_id)
        id_message = int(payload.message_id)
        id_emoji = None if not payload.emoji.id else int(payload.emoji.id)
        guild = self.bot.get_guild(payload.guild_id)
        msg_platform = int(os.getenv("NPL_MSG_PLATFORM"))
        msg_game = int(os.getenv("NPL_MSG_GAME"))
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
                message_ob = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                if not "TENEMOS DUELO CONFIRMADO" in message_ob.content:
                    return
                if not len(message_ob.mentions)==2:
                    return
                id_discord_a = int(message_ob.mentions[0].id)
                id_discord_b = int(message_ob.mentions[1].id)
                last_word = str.lower(remove_accents(message_ob.content.split()[-1]))
                days_ascii = self.bot.vars["days_ascii"]
                if not last_word in days_ascii:
                    return
                id_dia = days_ascii.index(last_word)
                # Quita roles de duelo del dia
                member_a = await guild.fetch_member(id_discord_a)
                member_b = await guild.fetch_member(id_discord_b)
                dia_str = self.bot.vars["days_hr"][id_dia]
                role_name_1 = "Duelo Confirmado "+remove_accents(str(dia_str))
                role_objt_1 = discord.utils.get(guild.roles,name=role_name_1)
                role_name_2 = "Retador "+remove_accents(str(dia_str))
                role_objt_2 = discord.utils.get(guild.roles,name=role_name_2)
                await member_a.remove_roles(role_objt_1,role_objt_2)
                await member_b.remove_roles(role_objt_1,role_objt_2)
                # Quita match de la base de datos
                db_con = sqlite3.connect(os.getenv("NPL_DB_PATH"))
                db_cur = db_con.cursor()
                db_cur.execute("delete from duelos where id_dia=? and ((id_discord_a=? and id_discord_b=?) or (id_discord_a=? and id_discord_b=?))",(id_dia,id_discord_a,id_discord_b,id_discord_b,id_discord_a))
                db_con.commit()
                db_con.close()
                await message_ob.delete()

    # Este evento se detona cuando alguien quita una reaccion a un mensaje
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        id_user = int(payload.user_id)
        id_message = int(payload.message_id)
        id_emoji = None if not payload.emoji.id else int(payload.emoji.id)
        guild = self.bot.get_guild(payload.guild_id)
        msg_platform = int(os.getenv("NPL_MSG_PLATFORM"))
        msg_game = int(os.getenv("NPL_MSG_GAME"))
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



# Necesario para cargar el cog
async def setup(bot):
    await bot.add_cog(ReactionsCog(bot))
