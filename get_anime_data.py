import asyncio
import os
import pickle
import timeit

import aiohttp
import uvloop

from schema import Anime, Genre, RateLimitError


MAL_BASE_URL = "https://api.myanimelist.net/v2"
JIKAN_BASE_URL = "https://api.jikan.moe"

JIKAN_GET_TOP_ANIME_REQ_PARAMS = {
    "limit": 25,  # 25 is max
    "sfw": "true",
}


async def jikan_get_genres() -> list[Genre]:
    async with aiohttp.ClientSession(JIKAN_BASE_URL) as session:
        async with session.get("/genres/anime") as response:
            genres = await response.json()
            return [Genre.parse(genre) for genre in genres.get("data", [])]


async def jikan_get_top_anime_page(page: int = 1) -> list[Anime]:
    try:
        async with aiohttp.ClientSession(JIKAN_BASE_URL) as session:
            async with session.get(
                "/v4/top/anime",
                params={"page": page} | JIKAN_GET_TOP_ANIME_REQ_PARAMS,
            ) as response:
                data = await response.json()

                if response.status == 429:
                    raise RateLimitError

                return [Anime.parse(anime) for anime in data.get("data")]
    except RateLimitError:
        await asyncio.sleep(3)
        return await jikan_get_top_anime_page(page)
    except Exception as e:
        await asyncio.sleep(10)
        print(f"retrying page {page} because of error {e}", page)
        return await jikan_get_top_anime_page(page)


async def jikan_get_top_anime(limit: int = 500) -> list[Anime]:
    animes = list()

    async with aiohttp.ClientSession(JIKAN_BASE_URL) as session:
        async with session.get(
            "/v4/top/anime", params={"limit": 1} | JIKAN_GET_TOP_ANIME_REQ_PARAMS
        ) as response:
            data = await response.json()
            total_pages = data["pagination"]["last_visible_page"]

    for paged_animes in asyncio.as_completed(
        [
            jikan_get_top_anime_page(page)
            for page in range(
                1,
                min(
                    total_pages + 1,
                    limit // JIKAN_GET_TOP_ANIME_REQ_PARAMS.get("limit", 25),
                ),
            )
        ]
    ):
        animes.extend(await paged_animes)

    # Instead of returning animes[:limit], return everything that was fetched
    return animes


async def get_image(url: str) -> bytes:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()
    except OSError as e:
        print(f"Error downloading image from {url}: {str(e)}")
        await asyncio.sleep(5)
        return await get_image(url)


async def download_anime_image(anime: Anime):
    fpath = f"images/{anime.mal_id}.jpg"

    if os.path.exists(fpath):
        return

    with open(fpath, "wb") as f:
        f.write(await get_image(anime.get_image_url()))


async def download_anime_images(animes: list[Anime]):
    tasks = [download_anime_image(anime) for anime in animes]
    await asyncio.gather(*tasks)


async def main():
    start_time = timeit.default_timer()

    animes_pkl = "animes.pkl"
    if os.path.exists(animes_pkl):
        print("loading animes from file")
        with open(animes_pkl, "rb") as f:
            animes = pickle.load(f)
    else:
        print("fetching animes from jikan api")
        animes = await jikan_get_top_anime(limit=15_000)

        # Save animes to a file as cache
        with open(animes_pkl, "wb") as f:
            pickle.dump(animes, f)

    anime_fetch_time = timeit.default_timer()

    print(f"downloading {len(animes)} images")
    await download_anime_images(animes)
    end_time = timeit.default_timer()
    print(
        "done after",
        end_time - start_time,
        "seconds. anime fetching took",
        anime_fetch_time - start_time,
        "seconds",
    )


if __name__ == "__main__":
    os.makedirs("images", exist_ok=True)
    uvloop.run(main())
