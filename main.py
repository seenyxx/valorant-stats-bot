from nextcord.embeds import Embed
from nextcord.activity import ActivityType, Activity
from nextcord.ext import commands
from yaml import load as load_yaml, Loader
from math import floor
from re import search
from random import randint
import api

def load_config():
    with open('config.yml') as file:
        data = file.read()
        parsed_data = load_yaml(data, Loader=Loader)
    return parsed_data

def add_empty_field(embed):
    embed.add_field(name='\u200b', value='\u200b', inline=True)

def add_act(act_name, data, embed: Embed):
    embed.add_field(name=act_name, value='```yml\nRank: {}\nWins: {}\nGames: {}\nWinrate: {:.1f}%```'.format(data['final_rank_patched'], data['wins'], data['number_of_games'], data['wins'] / data['number_of_games'] * 100))

def positive_or_negative(num):
    if num < 0:
        return ''
    else:
        return '+'

def random_display_for_bundle():
    random = randint(1,2)
    if random == 1:
        return 'displayIcon'
    else:
        return 'displayIcon2'

def calculate_game_acs(score, rounds):
    return score / rounds

def won_or_lose_game(player, blue):
    team = player['team'].lower()

    if blue['has_won'] and team == 'blue':
        return True
    elif not blue['has_won'] and team == 'red':
        return True
    else:
        return False

def format_rounds_win_lose(player_team):
    return '{}-{}'.format(player_team['rounds_won'], player_team['rounds_lost'])

def format_win_lose(result):
    if result:
        return 'Win'
    else:
        return 'Lose'

def format_game_kda(kills, deaths, assists):
    return '{} / {} / {}'.format(kills, deaths, assists)

def add_game(game_data, embed: Embed, rr_change):
    player = game_data['player']
    player_team = player['team'].lower()
    player_stats = player['stats']
    embed.add_field(
        name='**{} | {} | {} | {}**'.format(player['character'], game_data['map'], format_win_lose(won_or_lose_game(player, game_data['blue'])), '{}{}'.format(positive_or_negative(rr_change), rr_change)), 
        value='```yml\nScore: {}\nACS: {:.0f}\nKDA: {}\nAvg Damage/Round: {:.0f}\nRounds: {}\nStart: {}```'.format(format_rounds_win_lose(game_data[player_team]), calculate_game_acs(player_stats['score'], game_data['rounds_played']), format_game_kda(player_stats['kills'], player_stats['deaths'], player_stats['assists']), player['damage_made'] / game_data['rounds_played'], game_data['rounds_played'], game_data['game_start_patched']),
        inline=True
    )

def calculate_total_mmr_stats(seasons):
    wins = 0
    losses = 0
    games = 0

    for key, season in seasons.items():
        wins += season['wins']
        losses += (season['number_of_games'] - season['wins'])
        games += season['number_of_games']
    
    return {
        'wins': wins,
        'losses': losses,
        'games': games
    }

valorant_name_regex = '^.+#.+$'

config = load_config()

bot = commands.Bot(command_prefix=config['prefix'])

@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def ping(ctx):
    await ctx.reply('Pong! `{}ms`'.format(floor(bot.latency * 1000)))

@commands.cooldown(1, 15, commands.BucketType.user)
@bot.command(name='store', aliases=['bundle'])
async def val_store(ctx):
    bundle = api.get_store_bundle()
    
    if not bundle:
        return await ctx.reply('An error has occurred.')
    
    data = bundle['data']
    
    bundle_embed = Embed(title='**{}**'.format(data['displayName']), description='**{}**\n{}'.format(data['description'], data['extraDescription']), color=0x001b3b)
    bundle_embed.set_image(url=data[random_display_for_bundle()])

    await ctx.send(embed=bundle_embed)

@commands.cooldown(1, 15, commands.BucketType.user)
@bot.command(name='rank-history', aliases=['episodes', 'acts'])
async def mmr(ctx, *args):
    profile_text = ' '.join(args)
    await ctx.reply('Fetching Rank history for `{}` ...'.format(profile_text))

    if not search(valorant_name_regex, profile_text):
        return await ctx.reply('The valorant profile must be in the format `name#tag`')

    name_tag = profile_text.split('#')

    profile = api.get_profile(name_tag[0], name_tag[1])
    
    if not profile:
        return await ctx.reply('An error has occurred.')
    
    profile_data = profile['data']
    profile_card = profile_data['card']

    mmr = api.get_mmr(profile_data['region'], name_tag[0], name_tag[1])

    if not mmr:
        return await ctx.reply('An error has occurred.')
    
    mmr_data = mmr['data']
    seasons = mmr_data['by_season']

    profile_embed = Embed(title='Rank History for: **{}#{}**'.format(name_tag[0], name_tag[1]), color=0xF24D4E)
    
    profile_embed.set_author(name='{}#{}'.format(profile_data['name'], profile_data['tag']), icon_url=profile_card['small'])

    for key in seasons:
        add_act(key.upper(), seasons[key], profile_embed)


    total_stats_embed = Embed(title='', color=0xF24D4E)
    total_data = calculate_total_mmr_stats(seasons)

    total_stats_embed.add_field(name='Ranked Total Wins', value='```diff\n+ {}```'.format(total_data['wins']), inline=True)
    total_stats_embed.add_field(name='Ranked Total Losses', value='```diff\n- {}```'.format(total_data['losses']), inline=True)
    total_stats_embed.add_field(name='Ranked Winrate', value='```fix\n{:.2f}%```'.format((total_data['wins'] / total_data['games']) * 100), inline=True)
    
    
    await ctx.send(embed=profile_embed)
    await ctx.send(embed=total_stats_embed)

@commands.cooldown(1, 20, commands.BucketType.user)
@bot.command(name='competitive', aliases=['comp', 'ranked'])
async def comp_match_history(ctx, *args):
    profile_text = ' '.join(args)
    await ctx.reply('Fetching Competitive data for `{}` ...'.format(profile_text))

    if not search(valorant_name_regex, profile_text):
        return await ctx.reply('The valorant profile must be in the format `name#tag`')

    name_tag = profile_text.split('#')
    profile = api.get_profile(name_tag[0], name_tag[1])

    if not profile:
        return await ctx.reply('An error has occurred.')
    
    profile_data = profile['data']
    profile_card = profile_data['card']

    rr_changes = api.get_rr_changes(profile_data['region'], profile_data['name'], profile_data['tag'])

    if not rr_changes:
        return await ctx.reply('An error has occurred.')
    
    match_history = api.get_match_history(profile_data['region'], profile_data['name'], profile_data['tag'], profile_data['puuid'], 'competitive')

    comp_embed = Embed(title='Competitive History for: **{}#{}**'.format(name_tag[0], name_tag[1]), color=0x42f5b0)
    comp_embed.set_author(name='{}#{}'.format(profile_data['name'], profile_data['tag']), icon_url=profile_card['small'])

    i = 0
    for match in match_history:
        if len(rr_changes) - 1 < i:
            break

        add_game(match, comp_embed, rr_changes[i])
        i += 1
    
    

    mmr = api.get_mmr(profile_data['region'], name_tag[0], name_tag[1])

    if not mmr:
        return await ctx.reply('An error has occurred.')

    mmr_data = mmr['data']
    seasons = mmr_data['by_season']

    total_stats_embed = Embed(title='', color=0x42f5b0)
    total_data = calculate_total_mmr_stats(seasons)

    total_stats_embed.add_field(name='Ranked Total Wins', value='```diff\n+ {}```'.format(total_data['wins']), inline=True)
    total_stats_embed.add_field(name='Ranked Total Losses', value='```diff\n- {}```'.format(total_data['losses']), inline=True)
    total_stats_embed.add_field(name='Ranked Winrate', value='```fix\n{:.2f}%```'.format((total_data['wins'] / total_data['games']) * 100), inline=True)
    
    await ctx.send(embed=comp_embed)
    await ctx.send(embed=total_stats_embed)

@commands.cooldown(1, 20, commands.BucketType.user)
@bot.command(name='profile', aliases=['user', 'player'])
async def profile(ctx, *args):
    profile_text = ' '.join(args)
    await ctx.reply('Fetching Profile `{}` ...'.format(profile_text))

    if not search(valorant_name_regex, profile_text):
        return await ctx.reply('The valorant profile must be in the format `name#tag`')

    name_tag = profile_text.split('#')
    profile = api.get_profile(name_tag[0], name_tag[1])
    if not profile:
        print(profile)
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

    if not mmr:
        return await ctx.reply('An error has occurred.')

    mmr_data = mmr['data']
    current_data = mmr_data['current_data']
    current_rating = current_data['ranking_in_tier']
    current_rank = current_data['currenttierpatched']
    last_game_rating_change = current_data['mmr_change_to_last_game']
    seasons = mmr_data['by_season']

    add_empty_field(profile_embed)
    profile_embed.add_field(name='Current Rank', value='**```yml\n{}```**'.format(current_rank), inline=True)
    profile_embed.add_field(name='Current RR', value='```yml\n{}```'.format(current_rating), inline=True)
    profile_embed.add_field(name='Latest Game', value='```diff\n{}{}```'.format(positive_or_negative(last_game_rating_change), last_game_rating_change), inline=True)   

    total_data = calculate_total_mmr_stats(seasons)

    profile_embed.add_field(name='Ranked Total Wins', value='```diff\n+ {}```'.format(total_data['wins']), inline=True)
    profile_embed.add_field(name='Ranked Total Losses', value='```diff\n- {}```'.format(total_data['losses']), inline=True)
    profile_embed.add_field(name='Ranked Winrate', value='```fix\n{:.2f}%```'.format((total_data['wins'] / total_data['games']) * 100), inline=True)

    i = 0
    for key in seasons:
        i += 1
        add_act(key.upper(), seasons[key], profile_embed)
        if i == 2:
            break

    await ctx.send(embed=profile_embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = Embed(title='You cannot use this command yet! ⌚',description='Try again in **{:.2f} seconds**'.format(error.retry_after), color=0x001b3b)
        await ctx.send(embed=embed)
    else:
        print(error)

@bot.event
async def on_ready():
    print('Ready!')
    await bot.change_presence(activity=Activity(type=ActivityType.listening, name='{}help'.format(config['prefix'])))

bot.run(config['token'])