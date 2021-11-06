import requests
import json

def get_profile(name, tag):
    x = requests.get('https://api.henrikdev.xyz/valorant/v1/account/{}/{}'.format(name, tag))
    
    if (not x.status_code == 200):
        return False
    else:
        return x.json()

def get_mmr(region, name, tag):
    x = requests.get('https://api.henrikdev.xyz/valorant/v2/mmr/{}/{}/{}'.format(region, name, tag))
    
    if (not x.status_code == 200):
        return False
    else:
        return x.json()