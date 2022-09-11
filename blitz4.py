from http import client
from discord.ext import commands
import discord
import asyncio
import wargaming
import time
import datetime 
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *
from sqlalchemy.types import Integer, String, DateTime, BigInteger, Text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import openpyxl


wotb = wargaming.WoTB('API ID', region='asia', language='en')
engine = create_engine('')
table1 = Table('dataset.wwn_public')
Base = declarative_base()
Base2 = declarative_base()
SessionClass = sessionmaker(engine)
session = SessionClass()
id_count = 0

intents = discord.Intents.default()
intents.members = True 
client = discord.Client(intents=intents)


class wwn_public(Base):
    __tablename__ = "wwn_public"
    id = Column(Integer, nullable=False)
    ign = Column(Text, nullable=False)
    wargaming_id = Column(Integer, primary_key=True)
    clan = Column(String(5))
    discord_name = Column(Text,nullable=False)
    discord_id = Column(BigInteger, primary_key=True)
    date = Column(DateTime, nullable=False)
    discord_nick = Column(Text)

class wwn_blacklist(Base2):
    __tablename__ = "wwn_blacklist"
    id = Column(Integer, nullable=False)
    ign = Column(Text, nullable=False)
    wargaming_id = Column(Integer, primary_key=True)
    discord_id = Column(BigInteger, primary_key=True)
    reason = Column(Text, nullable=False)
    

class Blitz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @discord.ext.commands.has_guild_permissions(administrator = True)
    async def create(self,ctx):
        Base2.metadata.create_all(engine)

    @commands.command()
    async def add(self,ctx,author_ign):
        guild = ctx.guild
        member = ctx.author
    
        if (ctx.channel.id != 701429114128695357):
            await ctx.send(f"このチャンネルには送信できません。")
            return

        d_id = member.id
        serach_id = session.query(wwn_public).filter(wwn_public.discord_id==d_id).one_or_none()

        if (serach_id):
            embed=discord.Embed(title=f'同一ID登録エラー')
            embed.description = "同一アカウントでの再登録はできません。"
            embed.color = discord.Colour.red()
            await ctx.send(embed=embed)
            return


        player_data = wotb.account.list(search = author_ign)

        if player_data:
            await ctx.send(f"IGN検索中…")
        else:
            embed=discord.Embed(title=f'IGN検索エラー')
            embed.description = "IGNが見つかりませんでした"
            embed.color = discord.Colour.red()
            await ctx.send(embed=embed)
            return

        author_ign = player_data[0]["nickname"]
        user_id = player_data[0]["account_id"]
        player_clan = wotb.clans.accountinfo(account_id = user_id)

        if player_clan[user_id]["clan_id"]:    
            clan_p:int = player_clan[user_id]["clan_id"]
            clan_detail = wotb.clans.info(clan_id = clan_p)
            clan_tag = clan_detail[clan_p]["tag"]
        else:
            clan_p = 0
            clan_tag = None

        embed=discord.Embed(title=f'WoTBlitzアカウントデータ')
        embed.add_field(name='◇IGN', value=author_ign, inline=True)
        embed.add_field(name='◇クランタグ', value=clan_tag, inline=True)
        embed.color = discord.Color.blue()
        await ctx.send(embed=embed)
        async with ctx.channel.typing():

            date_now = datetime.datetime.now()
            pick_id = session.query(wwn_public.id).order_by(wwn_public.id.desc()).first()
            if pick_id is None:
                id_count = 1
            else:
                id_count = pick_id[0]
                id_count += 1

            user_data = wwn_public(id=id_count, ign=author_ign, wargaming_id=user_id, clan=clan_tag, discord_name=member.name, discord_id=member.id, date=date_now, discord_nick=member.nick)
            session.add(user_data)
            session.commit()

            guild = ctx.guild
            role_wwn_group = guild.get_role(688932130742337539)
            role_visitor = guild.get_role(688986060612698142)
            role_wwne = guild.get_role(693783330218442792)
            role_wwna = guild.get_role(703761772653445290)
            role_wwn = guild.get_role(945897222313226240)
            role_wwn2 = guild.get_role(945897305322696725)
            role_wwn3 = guild.get_role(945897438105976894)
            role_wwn4 = guild.get_role(945897551205396491)
            role_ign = guild.get_role(828124281577275392)
            role_sheri = guild.get_role(995583015113736192)
            #パブリック鯖

            await member.remove_roles(role_wwn)
            await member.remove_roles(role_wwn2)
            await member.remove_roles(role_wwn3)
            await member.remove_roles(role_wwn4)
            await member.remove_roles(role_wwne)
            await member.remove_roles(role_wwna)
            await member.remove_roles(role_wwn_group)
            await member.remove_roles(role_ign)
            await member.add_roles(role_visitor)

            if clan_p == 1845:
                await member.add_roles(role_wwn)
                await member.add_roles(role_wwn_group)
            elif clan_p == 6800:
                await member.add_roles(role_wwn2)
                await member.add_roles(role_wwn_group)
            elif clan_p == 29274:
                await member.add_roles(role_wwn3)
                await member.add_roles(role_wwn_group)
            elif clan_p == 44817:
                await member.add_roles(role_wwn4)
                await member.add_roles(role_wwn_group)
            elif clan_p == 34796:
                await member.add_roles(role_wwna)
                await member.add_roles(role_wwn_group)
            elif clan_p == 16297:
                await member.add_roles(role_wwne)
                await member.add_roles(role_wwn_group)
            else:
                await member.add_roles(role_visitor)

            
        serach_id = session.query(wwn_blacklist).filter(wwn_blacklist.discord_id==d_id).one_or_none()
        serach_ign = session.query(wwn_blacklist).filter(wwn_blacklist.wargaming_id==user_id).one_or_none()

        if(serach_id):
            await member.add_roles(role_sheri)
        elif(serach_ign):
            await member.add_roles(role_sheri)

        await ctx.send(f"ロールを付与しました。")
        await ctx.send(f"IGN: {author_ign}を登録しました")

    @commands.command()
    async def update(self,ctx):
        member = ctx.author
        d_id = member.id
        
        update_user = session.query(wwn_public).filter(wwn_public.discord_id==d_id).one_or_none()

        if (update_user == None):
            embed=discord.Embed(title=f'ID検索エラー')
            embed.description = "このアカウントは登録されていません。"
            embed.color = discord.Colour.red()
            await ctx.send(embed=embed)
            return
        
        update_id = update_user.wargaming_id
        player_data = wotb.account.info(account_id = update_id)

        await ctx.send(f"IGN検索中…")
        async with ctx.channel.typing():

            author_ign = player_data[update_id]["nickname"]
            player_clan = wotb.clans.accountinfo(account_id = update_id)

            if player_clan[update_id]["clan_id"]:    
                clan_p:int = player_clan[update_id]["clan_id"]
                clan_detail = wotb.clans.info(clan_id = clan_p)
                clan_tag = clan_detail[clan_p]["tag"]
            else:
                clan_p = 0
                clan_tag = None

            embed=discord.Embed(title=f'WoTBlitzアカウントデータ')
            embed.add_field(name='◇IGN', value=author_ign, inline=True)
            embed.add_field(name='◇クランタグ', value=clan_tag, inline=True)
            embed.color = discord.Color.blue()
            await ctx.send(embed=embed)

            update_user.ign = author_ign
            update_user.clan = clan_tag
            update_user.discord_name = member.name
            update_user.discord_nick = member.nick
            session.commit()

            guild = ctx.guild
            role_wwn_group = guild.get_role(688932130742337539)
            role_visitor = guild.get_role(688986060612698142)
            role_wwne = guild.get_role(693783330218442792)
            role_wwna = guild.get_role(703761772653445290)
            role_wwn = guild.get_role(945897222313226240)
            role_wwn2 = guild.get_role(945897305322696725)
            role_wwn3 = guild.get_role(945897438105976894)
            role_wwn4 = guild.get_role(945897551205396491)
            role_ign = guild.get_role(828124281577275392)
            #パブリック鯖

            await member.remove_roles(role_wwn)
            await member.remove_roles(role_wwn2)
            await member.remove_roles(role_wwn3)
            await member.remove_roles(role_wwn4)
            await member.remove_roles(role_wwne)
            await member.remove_roles(role_wwna)
            await member.remove_roles(role_wwn_group)
            await member.remove_roles(role_ign)
            await member.add_roles(role_visitor)

            if clan_p == 1845:
                await member.add_roles(role_wwn)
                await member.add_roles(role_wwn_group)
            elif clan_p == 6800:
                await member.add_roles(role_wwn2)
                await member.add_roles(role_wwn_group)
            elif clan_p == 29274:
                await member.add_roles(role_wwn3)
                await member.add_roles(role_wwn_group)
            elif clan_p == 44817:
                await member.add_roles(role_wwn4)
                await member.add_roles(role_wwn_group)
            elif clan_p == 34796:
                await member.add_roles(role_wwna)
                await member.add_roles(role_wwn_group)
            elif clan_p == 16297:
                await member.add_roles(role_wwne)
                await member.add_roles(role_wwn_group)
            else:
                await member.add_roles(role_visitor)

        await ctx.send(f"ロールを付与しました。")

        await ctx.send(f"{author_ign}を更新しました")

    @commands.command()
    @discord.ext.commands.has_guild_permissions(administrator = True)
    async def update_all(self,ctx):
        guild = ctx.guild

        id_count = session.query(wwn_public.id).order_by(wwn_public.id.desc()).first()
        id2 = id_count[0]
        for count in range(id2):
            update_user = session.query(wwn_public).filter(wwn_public.id==count).one_or_none()

            if (update_user == None):
                continue
            
            update_id = update_user.wargaming_id
            player_data = wotb.account.info(account_id = update_id)

            async with ctx.channel.typing():

                author_ign = player_data[update_id]["nickname"]
                player_clan = wotb.clans.accountinfo(account_id = update_id)

                if player_clan[update_id]["clan_id"]:    
                    clan_p:int = player_clan[update_id]["clan_id"]
                    clan_detail = wotb.clans.info(clan_id = clan_p)
                    clan_tag = clan_detail[clan_p]["tag"]
                else:
                    clan_p = 0
                    clan_tag = None

                member = guild.get_member(update_user.discord_id)
                if (member == None):
                    session.query(wwn_public).filter(wwn_public.discord_id==update_user.discord_id).delete()
                    await ctx.send(f"{author_ign}：サーバーにいないため削除しました")
                    session.commit()
                    continue

                if (update_user.ign==author_ign and update_user.clan==clan_tag and update_user.discord_name==member.name and update_user.discord_nick==member.nick):
                    continue
                
                update_user.ign = author_ign
                update_user.clan = clan_tag
                update_user.discord_name = member.name
                update_user.discord_nick = member.nick
                session.commit()

                role_wwn_group = guild.get_role(688932130742337539)
                role_visitor = guild.get_role(688986060612698142)
                role_wwne = guild.get_role(693783330218442792)
                role_wwna = guild.get_role(703761772653445290)
                role_wwn = guild.get_role(945897222313226240)
                role_wwn2 = guild.get_role(945897305322696725)
                role_wwn3 = guild.get_role(945897438105976894)
                role_wwn4 = guild.get_role(945897551205396491)
                role_ign = guild.get_role(828124281577275392)
                #パブリック鯖

                await member.remove_roles(role_wwn)
                await member.remove_roles(role_wwn2)
                await member.remove_roles(role_wwn3)
                await member.remove_roles(role_wwn4)
                await member.remove_roles(role_wwne)
                await member.remove_roles(role_wwna)
                await member.remove_roles(role_wwn_group)
                await member.remove_roles(role_ign)
                await member.add_roles(role_visitor)

                if clan_p == 1845:
                    await member.add_roles(role_wwn)
                    await member.add_roles(role_wwn_group)
                elif clan_p == 6800:
                    await member.add_roles(role_wwn2)
                    await member.add_roles(role_wwn_group)
                elif clan_p == 29274:
                    await member.add_roles(role_wwn3)
                    await member.add_roles(role_wwn_group)
                elif clan_p == 44817:
                    await member.add_roles(role_wwn4)
                    await member.add_roles(role_wwn_group)
                elif clan_p == 34796:
                    await member.add_roles(role_wwna)
                    await member.add_roles(role_wwn_group)
                elif clan_p == 16297:
                    await member.add_roles(role_wwne)
                    await member.add_roles(role_wwn_group)
                else:
                    await member.add_roles(role_visitor)

            await ctx.send(f"{author_ign}を更新しました")
        

    @commands.command()
    async def delete(self,ctx):
        async with ctx.channel.typing():
            member = ctx.author
            delete_id = member.id
            session.query(wwn_public).filter(wwn_public.discord_id==delete_id).delete()
            session.commit()

            guild = ctx.guild
            role_wwn_group = guild.get_role(688932130742337539)
            role_visitor = guild.get_role(688986060612698142)
            role_wwne = guild.get_role(693783330218442792)
            role_wwna = guild.get_role(703761772653445290)
            role_wwn = guild.get_role(945897222313226240)
            role_wwn2 = guild.get_role(945897305322696725)
            role_wwn3 = guild.get_role(945897438105976894)
            role_wwn4 = guild.get_role(945897551205396491)
            role_ign = guild.get_role(828124281577275392)
            #パブリック鯖

            await member.remove_roles(role_wwn)
            await member.remove_roles(role_wwn2)
            await member.remove_roles(role_wwn3)
            await member.remove_roles(role_wwn4)
            await member.remove_roles(role_wwne)
            await member.remove_roles(role_wwna)
            await member.remove_roles(role_wwn_group)
            await member.remove_roles(role_visitor)
            await member.add_roles(role_ign)

        await ctx.send(f"{member.name}の登録データを削除しました")

    @commands.command()
    @discord.ext.commands.has_guild_permissions(administrator = True)
    async def black_add(self,ctx,bl_ign,bl_d_id,bl_reason):
        guild = ctx.guild
        member = ctx.author
    
        if (ctx.channel.id != 477671088751378492):
            await ctx.send(f"このチャンネルには送信できません。")
            return
        
        serach_id = session.query(wwn_blacklist).filter(wwn_blacklist.discord_id==bl_d_id).one_or_none()

        if (serach_id):
            embed=discord.Embed(title=f'同一ID登録エラー')
            embed.description = "そのアカウントはすでに登録されています"
            embed.color = discord.Colour.red()
            await ctx.send(embed=embed)
            return


        player_data = wotb.account.list(search = bl_ign)

        if player_data:
            await ctx.send(f"IGN検索中…")
        else:
            embed=discord.Embed(title=f'IGN検索エラー')
            embed.description = "IGNが見つかりませんでした"
            embed.color = discord.Colour.red()
            await ctx.send(embed=embed)
            return

        bl_ign = player_data[0]["nickname"]
        bl_id = player_data[0]["account_id"]

        async with ctx.channel.typing():
            date_now = datetime.datetime.now()
            pick_id = session.query(wwn_blacklist.id).order_by(wwn_blacklist.id.desc()).first()
            if pick_id is None:
                id_count = 1
            else:
                id_count = pick_id[0]
                id_count += 1

            user_data = wwn_blacklist(id=id_count, ign=bl_ign, wargaming_id=bl_id, discord_id=bl_d_id, reason=bl_reason)
            session.add(user_data)
            session.commit()
        await ctx.send("ブラックリストに登録しました")

    @commands.command()
    @discord.ext.commands.has_guild_permissions(administrator = True)
    async def black_update(self,ctx,bl_id,bl_d_id):
        member = ctx.author
        d_id = member.id

        update_user = session.query(wwn_blacklist).filter(wwn_blacklist.wargaming_id==bl_id).one_or_none()

        if (update_user == None):
            embed=discord.Embed(title=f'ID検索エラー')
            embed.description = "このアカウントは登録されていません。"
            embed.color = discord.Colour.red()
            await ctx.send(embed=embed)
            return
        
        update_id = update_user.wargaming_id
        player_data = wotb.account.info(account_id = update_id)

        await ctx.send(f"IGN検索中…")
        async with ctx.channel.typing():

            author_ign = player_data[update_id]["nickname"]

            update_user.ign = author_ign
            update_user.discord_id = bl_d_id
            session.commit()

        await ctx.send("ブラックリストを更新しました")



    @commands.command()
    async def command_help(self,ctx):
        embed=discord.Embed(title=f'コマンド一覧')
        embed.add_field(name="!bcn add IGN", value="IGNを登録します。\n例) !bcn add Azumina373", inline=False)
        embed.add_field(name="!bcn update", value="登録されている情報を更新します。\nIGNは必要ありません",inline=False)
        embed.add_field(name="!bcn delete", value="登録した自分のデータを削除します。\nロールも消えます。\nIGNは必要ありません",inline=False)
        embed.color = discord.Colour.blue()
        await ctx.send(embed=embed)

    @commands.command()
    @discord.ext.commands.has_guild_permissions(administrator = True)
    async def export(self,ctx):
        if (ctx.channel.id != 477671088751378492):
            await ctx.send(f"このチャンネルには送信できません。")
            return
        
        guild = ctx.guild
        df = pd.read_sql(sql='SELECT * FROM wwn_public;', con=engine)
        df['wargaming_id'] = df['wargaming_id'].astype(str)
        df['discord_id'] = df['discord_id'].astype(str)

        for num in range(len(df)):
            num_count = num - 1
            wgid_sell = df.iat[num_count, 2]
            d_id_sell = df.iat[num_count, 5]
            quote_wgid = '\"' + wgid_sell + '\"'
            quote_d_id = '\"' + d_id_sell + '\"'
            df.iat[num_count, 2] = quote_wgid
            df.iat[num_count, 5] = quote_d_id
            #IDのテキスト化

        df.to_excel('wwn_public.xlsx', index=False)
        await ctx.send(file=discord.File(fp="wwn_public.xlsx"))

        

    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send(" パラメーターの形式が違います")
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(" パラメーターの数が足りません")


    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx, module_name):
        await ctx.send(f" モジュール{module_name} の再読み込みを開始します。")
        try:
            self.bot.reload_extension(module_name)
            await ctx.send(f" モジュール{module_name} の再読み込みを終了しました。")
        except (commands.errors.ExtensionNotLoaded, commands.errors.ExtensionNotFound,commands.errors.NoEntryPointError, commands.errors.ExtensionFailed) as e:
            await ctx.send(f" モジュール{module_name} の再読み込みに失敗しました。理由：{e}")
            return


def setup(bot):
    bot.add_cog(Blitz(bot))