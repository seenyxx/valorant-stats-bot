import requests

port = '5000'
host = '127.0.0.1:{}'.format(port)

def get_profile(name, tag):
    req = requests.get('{}/valorant/user?name={}&tag{}'.format(host, name, tag))
    
    if not req.json()['status'] == 200:
        return False
    else:
        return req.json()

def get_mmr(region, name, tag):
    req = requests.get('{}/valorant/mmr?region={}&name={}&tag={}'.format(host, region, name, tag))
    
    if not req.json()['status'] == 200:
        return False
    else:
        return req.json()

def get_store_bundle():
    req = requests.get('{}/valorant/store-featured'.format(host))
    
    if not req.json()['status'] == 200:
        return False
    else:
        data = req.json()['data']
        featured = data['FeaturedBundle']
        bundle = featured['Bundle']
        asset_id = bundle['DataAssetID']

        bundle_req = requests.get('https://valorant-api.com/v1/bundles/{}'.format(asset_id))

        if (not bundle_req.status_code == 200):
            return False

        return bundle_req.json()

def get_match_history(region, name, tag, puuid, filter):
    req = requests.get('{}/valorant/matches?region={}&name={}&tag={}filter={}&size=10'.format(host, region, name, tag, filter))

    if not req.json()['status'] == 200:
        return False
    else:
        data = req.json()['data']
        games = []

        for game in data:
            meta = game['metadata']
            teams = game['teams']
            players = game['players']
            all_players = players['all_players']

            games.append({
                'map': meta['map'],
                'game_version': meta['game_version'],
                'rounds_played': meta['rounds_played'],
                'mode': meta['mode'],
                'season_id': meta['season_id'],
                'matchid': meta['matchid'],
                'game_start': meta['game_start'],
                'game_start_patched': meta['game_start_patched'],
                'blue': teams['blue'],
                'red': teams['red'],
                'player': next((player for player in all_players if player['puuid'] == puuid), None),
                'all_players': players
            })

        return games

def get_rr_changes(region, name, tag):
    req = requests.get('{}/valorant/mmr-history?region={}&name={}&tag={}'.format(host, region, name, tag))

    if not req.json()['status'] == 200:
        return False
    else:
        mmr_changes = []

        data = req.json()['data']

        for change in data:
            mmr_changes.append(change['mmr_change_to_last_game'])

        return mmr_changes