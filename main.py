import random
import re
from typing import Optional

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

import utils

SONGS = {
    "a": "6WH0LHM2vFBLpmU5RFdDh2",
    "i": "0doOvUe6IiDVGBnvdH5VQF",
}


class SpotifyPoem:
    def __init__(self, merge: Optional[str] = None):
        self.merge = merge
        load_dotenv()
        scope = "playlist-modify-public"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        with open("song.txt", encoding="utf-8") as f:
            if merge:
                pattern = rf"\b{merge}\b|[A-Za-zÀ-ú]+(?:\'[a-z]+)?"
                self.words = re.findall(pattern, f.read())
            else:
                self.words = f.read().split()

    def get_track(self, search: str) -> Optional[str]:
        if self.merge and self.merge in search and self.merge != search:
            return
        search = search.lower()
        sanitized = utils.sanitize(search)

        result = SONGS.get(sanitized)
        if result:
            return result

        results = self.sp.search(f"track:{search}", limit=50)
        ids = set()
        while results and not ids:
            for item in results["tracks"]["items"]:
                if sanitized == utils.sanitize(item["name"].lower()):
                    ids.add(item["id"])
            if results["tracks"]["next"]:
                results = self.sp.next(results["tracks"])
            elif " " not in search and results["tracks"]["offset"] < 900:
                # not using track: gives better results
                results = self.sp.search(
                    f"{search}", limit=50, offset=results["tracks"]["offset"] + 50
                )
            else:
                results = None
        if ids:
            return random.choice(list(ids))

    def generate_tracks(self):
        tracks = []
        index = 0
        while index < len(self.words):
            track = False
            for i in list(range(3, -1, -1)):
                if index + i < len(self.words):
                    search = " ".join(self.words[index : index + i + 1])
                    track = self.get_track(search)
                    if track:
                        print(search, track)
                        tracks.append(f"spotify:track:{track}")
                        index += i
                        track = True
                        break
            if not track:
                print(self.words[index])
            index += 1
        return tracks

    def create_playlist(self):
        tracks = self.generate_tracks()
        create = self.sp.user_playlist_create(name="poem", user=self.sp.me()["id"])
        playlist_id = create["id"]
        for group in utils.grouper(tracks, 100):
            group = [x for x in group if x is not None]
            self.sp.playlist_add_items(playlist_id=playlist_id, items=group)


if __name__ == "__main__":
    poet = SpotifyPoem(merge="love you twice")
    print(poet.words)
    poet.create_playlist()
