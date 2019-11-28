import deezer
from deezpy import downloadDeezer
import deezpy
import configparser
from mutagen.easyid3 import EasyID3


class DeezerHandler:
    def __init__(self):
        self.client = deezer.Client()

    def get_artist(self, artist_name):
        result_artists = self.client.advanced_search(
            {"artist": artist_name}, relation="artist"
        )

        return result_artists

    def get_albums_of_artist(self, artist_id):
        return self.client.get_artist(artist_id).get_albums()

    def get_top_songs_of_artist(self, artist_id):
        return self.client.get_artist(artist_id).get_top()

    def get_album(self, album_name):
        result_albums = self.client.advanced_search(
            {"album": album_name}, relation="album"
        )
        return result_albums

    def get_album_songs(self, album_id):
        return self.client.get_album(album_id).get_tracks()

    def get_song(self, song_name):
        result_songs = self.client.search(song_name)
        return result_songs

    def get_song_details(self, song_id):
        song = self.client.get_track(song_id)
        song_data = song.asdict()
        return song_data

    def get_full_track(self, song_id):
        song = self.client.get_track(song_id)
        return song

    def download_url(self, url):
        deezpy.init()
        items = downloadDeezer(url)
        if "track" in url:
            track_id = url.split("/")[-1]

        if isinstance(items, list):
            for link in items:
                audio = EasyID3(link)
        else:
            audio = EasyID3(items)
            for key, value in self.get_song_details(track_id).items():
                if key == 'contributors':
                    l = []
                    for contributor in value:
                        l.append(contributor["name"])
                    audio['artist'] = l
            audio.save()

        return items



d = DeezerHandler()
