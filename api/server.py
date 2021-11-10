import time
from flask import Flask, request, jsonify
import pickledb
import requests

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

db = pickledb.load('server.db', True)

@app.route('/valorant/user')
def get_profile():
    username = request.args.get('name')
    tag = request.args.get('tag')
    db_query = 'user:{}:{}'.format(username, tag)

    if db.exists(db_query):
        lastTime = db.get(db_query)
        now = time.time()
        if now - lastTime > 900:
            req = requests.get('https://api.henrikdev.xyz/valorant/v1/account/{}/{}'.format(username, tag))
            db.set(db_query, now)
            return jsonify(req.json())
        elif db.exists('{}:data'.format(db_query)):
            return jsonify(db.get('{}:data'.format(db_query)))
        else:
            db.set(db_query, now)
            req = requests.get('https://api.henrikdev.xyz/valorant/v1/account/{}/{}'.format(username, tag))
            return jsonify(req.json())
    else:
        req = requests.get('https://api.henrikdev.xyz/valorant/v1/account/{}/{}'.format(username, tag))
        db.set(db_query, time.time())
        return jsonify(req.json())

@app.route('/valorant/mmr-history')
def get_mmr_hist():
    username = request.args.get('name')
    tag = request.args.get('tag')
    region = request.args.get('region')

    db_query = 'mmrhist:{}:{}:{}'.format(region, username, tag)

    if db.exists(db_query):
        lastTime = db.get(db_query)
        now = time.time()
        if now - lastTime > 1500:
            req = requests.get('https://api.henrikdev.xyz/valorant/v1/mmr-history/{}/{}/{}'.format(region, username, tag))
            db.set(db_query, now)
            return jsonify(req.json())
        elif db.exists('{}:data'.format(db_query)):
            return jsonify(db.get('{}:data'.format(db_query)))
        else:
            db.set(db_query, now)
            req = requests.get('https://api.henrikdev.xyz/valorant/v1/mmr-history/{}/{}/{}'.format(region, username, tag))
            return jsonify(req.json())
    else:
        req = requests.get('https://api.henrikdev.xyz/valorant/v1/mmr-history/{}/{}/{}'.format(region, username, tag))
        db.set(db_query, time.time())
        return jsonify(req.json())

@app.route('/valorant/matches')
def get_match_hist():
    username = request.args.get('name')
    tag = request.args.get('tag')
    region = request.args.get('region')
    filter = request.args.get('filter')

    db_query = 'matchhist:{}:{}:{}:{}'.format(region, username, tag, filter)

    if db.exists(db_query):
        lastTime = db.get(db_query)
        now = time.time()
        if now - lastTime > 1500:
            req = requests.get('https://api.henrikdev.xyz/valorant/v3/matches/{}/{}/{}?filter={}&size=10'.format(region, username, tag, filter))
            db.set(db_query, now)
            return jsonify(req.json())
        elif db.exists('{}:data'.format(db_query)):
            return jsonify(db.get('{}:data'.format(db_query)))
        else:
            db.set(db_query, now)
            req = requests.get('https://api.henrikdev.xyz/valorant/v3/matches/{}/{}/{}?filter={}&size=10'.format(region, username, tag, filter))
            return jsonify(req.json())
    else:
        req = requests.get('https://api.henrikdev.xyz/valorant/v3/matches/{}/{}/{}?filter={}&size=10'.format(region, username, tag, filter))
        db.set(db_query, time.time())
        return jsonify(req.json())

@app.route('/valorant/store-featured')
def get_bundle():
    db_query = 'bundle'

    if db.exists(db_query):
        lastTime = db.get(db_query)
        now = time.time()
        if now - lastTime > 21600:
            req = requests.get('https://api.henrikdev.xyz/valorant/v1/store-featured')
            db.set(db_query, now)
            return jsonify(req.json())
        elif db.exists('{}:data'.format(db_query)):
            return jsonify(db.get('{}:data'.format(db_query)))
        else:
            db.set(db_query, now)
            req = requests.get('https://api.henrikdev.xyz/valorant/v1/store-featured')
            return jsonify(req.json())
    else:       
        req = requests.get('https://api.henrikdev.xyz/valorant/v1/store-featured')
        db.set(db_query, time.time())
        return jsonify(req.json())

@app.route('/valorant/mmr')
def get_mmr():
    username = request.args.get('name')
    tag = request.args.get('tag')
    region = request.args.get('region')

    db_query = 'mmr:{}:{}:{}'.format(region, username, tag)

    if db.exists(db_query):
        lastTime = db.get(db_query)
        now = time.time()
        if now - lastTime > 900:
            req = requests.get('https://api.henrikdev.xyz/valorant/v2/mmr/{}/{}/{}'.format(region, username, tag))
            db.set(db_query, now)
            return jsonify(req.json())
        elif db.exists('{}:data'.format(db_query)):
            return jsonify(db.get('{}:data'.format(db_query)))
        else:
            db.set(db_query, now)
            req = requests.get('https://api.henrikdev.xyz/valorant/v2/mmr/{}/{}/{}'.format(region, username, tag))
            return jsonify(req.json())
    else:
        req = requests.get('https://api.henrikdev.xyz/valorant/v2/mmr/{}/{}/{}'.format(region, username, tag))
        db.set(db_query, time.time())
        return jsonify(req.json())
