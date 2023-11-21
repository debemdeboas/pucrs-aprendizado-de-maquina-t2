from dataclasses import dataclass
from typing import Any


class RateLimitError(Exception):
    pass


@dataclass
class Genre:
    mal_id: int
    mal_url: str
    name: str

    def __hash__(self) -> int:
        return self.mal_id

    @staticmethod
    def parse(genre: dict) -> "Genre":
        return Genre(
            mal_id=genre["mal_id"],
            mal_url=genre["url"],
            name=genre["name"],
        )
        
    def __repr__(self) -> str:
        return self.name


@dataclass
class Anime:
    mal_id: int
    mal_url: str
    title: str
    images: dict[str, dict[str, str]]
    genres: set[Genre]
    source: str

    def get_image_url(self) -> str:
        if url := self.images["jpg"].get(
            "large_image_url", self.images["jpg"].get("image_url")
        ):
            return url
        raise ValueError(
            f"No image URL found for anime ID {self.mal_id} ({self.title})"
        )

    @staticmethod
    def parse(anime: dict[str, Any]) -> "Anime":
        # The 'genres' list is a composition of the following keys:
        # - themes
        # - genres
        # - explicit genres
        # - demographics

        genres: set[Genre] = set()
        genres.update(Genre.parse(genre) for genre in anime.get("themes", []))
        genres.update(Genre.parse(genre) for genre in anime.get("genres", []))
        genres.update(Genre.parse(genre) for genre in anime.get("explicit_genres", []))
        genres.update(Genre.parse(genre) for genre in anime.get("demographics", []))

        return Anime(
            mal_id=anime["mal_id"],
            mal_url=anime["url"],
            title=anime["titles"][0]["title"],
            images=anime["images"],
            genres=genres,
            source=anime.get("source", ""),
        )
