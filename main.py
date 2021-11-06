from nextcord.embeds import Embed
from nextcord.ext import commands
from yaml import load as load_yaml, Loader
from math import floor
from re import search
import api

def load_config():
    with open('config.yml') as file:
        data = file.read()
        parsed_data = load_yaml(data, Loader=Loader)
    return parsed_data

def add_empty_field(embed):
    embed.add_field(name='\u200b', value='\u200b', inline=True)

def positive_or_negative(num):
    if (num < 0):
        return '-'
    else:
        return '+'

valorant_name_regex = '^.+#.+$'

config = load_config()

bot = commands.Bot(command_prefix=config['prefix'])

@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def ping(ctx):
    await ctx.reply('Pong! `{}ms`'.format(floor(bot.latency * 1000)))

@commands.cooldown(1, 8, commands.BucketType.user)
@bot.command()
async def profile(ctx, *args):
    profile_text = ' '.join(args)
    await ctx.reply('Fetching Profile `{}` ...'.format(profile_text))

    if (not search(valorant_name_regex, profile_text)):
        return await ctx.reply('The valorant profile must be in the format `name#tag`')

    name_tag = profile_text.split('#')
    profile = api.get_profile(name_tag[0], name_tag[1])
    if (not profile):
        return await ctx.reply('An error has occurred.')
    
    profile_data = profile['data']
    profile_card = profile_data['card']

    profile_embed = Embed(title='Stats for: **{}#{}**'.format(profile_data['name'], profile_data['tag']), color=0xF24D4E)
    
    profile_embed.set_thumbnail(url=profile_card['small'])
    profile_embed.add_field(name='Level', value='**```fix\n{}```**'.format(profile_data['account_level']), inline=True)
    profile_embed.add_field(name='Region', value='```\n{}```'.format(profile_data['region'].upper()), inline=True)
    profile_embed.set_author(name='{}#{}'.format(profile_data['name'], profile_data['tag']), icon_url=profile_card['small'])
    profile_embed.set_footer(text='Last updated {}'.format(profile_data['last_update']))

    mmr = api.get_mmr(profile_data['region'], name_tag[0], name_tag[1])

    mmr_data = mmr['data']
    current_data = mmr_data['current_data']
    current_rating = current_data['ranking_in_tier']
    current_rank = current_data['currenttierpatched']
    last_game_rating_change = current_data['mmr_change_to_last_game']

    add_empty_field(profile_embed)
    profile_embed.add_field(name='Current Rank', value='**```yml\n{}```**'.format(current_rank), inline=True)
    profile_embed.add_field(name='Current RR', value='```yml\n{}```'.format(current_rating), inline=True)
    profile_embed.add_field(name='Latest Game', value='```diff\n{} {}```'.format(positive_or_negative(last_game_rating_change), last_game_rating_change), inline=True)   
    await ctx.send(embed=profile_embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = Embed(title='You cannot use this command yet! ⌚',description='Try again in **{:.2f} seconds**'.format(error.retry_after), color=0x001b3b)
        await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print('Ready!')

bot.run(config['token'])