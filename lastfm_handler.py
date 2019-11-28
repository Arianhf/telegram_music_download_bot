import requests
import json

with open('config.json') as json_config_file:
    json_config = json.load(json_config_file)

API_KEY = json_config['LASTFM_API_KEY']


def get_tags(artist, title):
    # search_result = (requests.get(f"http://ws.audioscrobbler.com/2.0/?method=track.search&track={artist}%20{title}&api_key={API_KEY}&format=json")).json()
    song_data = (requests.get(f"http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={API_KEY}&artist={artist}&track={title}&format=json")).json()
    #print(song_data)
    try:
        tags = []
        for item in song_data['track']['toptags']['tag']:
            tags.append(item['name'])
        return tags
    except:
        return None


get_tags('adele','hello')
