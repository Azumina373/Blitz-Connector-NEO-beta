from discord.ext import commands
import discord
import config
import asyncio
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!bcn ", intents=intents)


@bot.event
async def on_ready():
    print("on_ready")

@bot.event
async def on_message(message):
    if message.author == bot.user:
            return

    await bot.process_commands(message)

@bot.command()
async def guild_info(ctx):
    from datetime import timedelta
    guild = ctx.guild
    member_count = guild.member_count
    user_count = sum(1 for member in guild.members if not member.bot)
    bot_count = sum(1 for member in guild.members if member.bot)
    guild_name = guild.name
    guild_id = guild.id
    guild_owner = guild.owner
    guild_create = guild.created_at + timedelta(hours=9)

    embed=discord.Embed(title=f'メンバー数')
    embed.add_field(name='◇サーバー名', value=guild_name, inline=True)
    embed.add_field(name='◇サーバーID', value=guild_id, inline=True)
    embed.add_field(name='◇サーバーオーナー', value=guild_owner, inline=True)
    embed.add_field(name='◇作成日', value=guild_create, inline=True)
    embed.add_field(name='◇メンバー数', value=member_count, inline=True)
    embed.add_field(name='◇ユーザー数', value=user_count, inline=True)
    embed.add_field(name='◇bot数', value=bot_count, inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def get_id(ctx):
    member = ctx.author
    dis_id = member.id
    await ctx.send(dis_id)
    

bot.load_extension("blitz4")
bot.run(config.TOKEN)