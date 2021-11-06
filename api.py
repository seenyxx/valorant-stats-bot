import requests
import json

def get_profile(name, tag):
    req = requests.get('https://api.henrikdev.xyz/valorant/v1/account/{}/{}'.format(name, tag))
    
    if (not req.status_code == 200):
        return False
    else:
        return req.json()

def get_mmr(region, name, tag):
    req = requests.get('https://api.henrikdev.xyz/valorant/v2/mmr/{}/{}/{}'.format(region, name, tag))
    
    if (not req.status_code == 200):
        return False
    else:
        return req.json()

def get_store_bundle():
    req = requests.get('https://api.henrikdev.xyz/valorant/v1/store-featured')
    
    if (not req.status_code == 200):
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
