from nextcord.embeds import Embed
from nextcord.ext import commands
from yaml import load as load_yaml, Loader
from math import floor
import pickledb

db = pickledb.load('data.db', True)

def load_config():
    with open('config.yml') as file:
        data = file.read()
        parsed_data = load_yaml(data, Loader=Loader)
    return parsed_data



config = load_config()

bot = commands.Bot(command_prefix=config['prefix'])

@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def ping(ctx):
    await ctx.reply('Pong! `{}ms`'.format(floor(bot.latency * 1000)))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = Embed(title='You cannot use this command yet! ⌚',description='Try again in **{:.2f} seconds**'.format(error.retry_after), color=0x001b3b)
        await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print('Ready!')

bot.run(config['token'])