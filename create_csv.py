import pickle
import os
import sys
import pandas as pd

from schema import Anime, Genre

ERR_BASE = 1
ERR_NO_PICKLE = ERR_BASE + 1
ERR_INVALID_PICKLE = ERR_NO_PICKLE + 1

def main(animes: list[Anime]):
    # Create a CSV file with the following columns:
    # - anime ID
    # - anime title
    # - anime URL
    # - image path (local)
    # - genres (comma-separated)
    
    df = pd.DataFrame(animes)

    for key in ("source", "title"):
        df[key] = df[key].apply(str.lower)

    df = df.drop(["images", "source"], axis=1)
    df["img_path"] = df["mal_id"].apply(lambda x: f"images/{x}.jpg")
    df["genres"] = df["genres"].apply(lambda s: sorted(list(s), key=(lambda x: x.name)))

    df.to_csv("animes.csv", index=False)


if __name__ == "__main__":
    if not os.path.exists("animes.pkl"):
        print("couldn't find animes.pkl. did you run 'get_anime_data.py'?")
        sys.exit(ERR_NO_PICKLE)

    with open("animes.pkl", "rb") as f:
        animes = pickle.load(f)

    if not isinstance(animes, list) or not isinstance(animes[0], Anime):
        print("animes.pkl is invalid. did you run 'get_anime_data.py'?")
        sys.exit(ERR_INVALID_PICKLE)

    main(animes)
