# ToDo 1: Move to file_utilities.py
import json
import os
import urllib.request
import urllib.error
from constants import POETRYDB_URL, CACHE_FILENAME
from models import Sonnet, Configuration, SearchResult
from typing import List

#created class printing in file_utilities
class Printing:

    @staticmethod
    def print_results(
            query: str,
            results: List[SearchResult],
            highlight: bool,
            hl_mode: str = "DEFAULT",
            query_time_ms: float | None = None,
    ) -> None:
        total_docs = len(results)
        matched = [r for r in results if r.matches > 0]

        line = f'{len(matched)} out of {total_docs} sonnets contain "{query}".'
        if query_time_ms is not None:
            line += f" Your query took {query_time_ms:.2f}ms."
        print(line)

        for idx, r in enumerate(matched, start=1):
            # ToDo 0: From here on move the printing code to SearchResult.print(...)
            #         You should then be able to call r.print(idx, highlight)
            r.print(idx, total_docs, highlight, hl_mode)



class Paths:
    @staticmethod
    def module_relative_path(name: str) -> str:
        """Return absolute path for a file next to this module."""
        return os.path.join(os.path.dirname(__file__), name)

# ToDo 1: Move to file_utilities.py
class Loading:

    # ToDo 1: Moved to file_utilities.py
    DEFAULT_CONFIG = Configuration()

    # ToDo 1: Move to file_utilities.py
    @staticmethod
    def fetch_sonnets_from_api() -> List[Sonnet]:
        """
        Call the PoetryDB API (POETRYDB_URL), decode the JSON response and
        convert it into a list of dicts.

        - Use only the standard library (urllib.request).
        - PoetryDB returns a list of poems.
        - You can add error handling: raise a RuntimeError (or print a helpful message) if something goes wrong.
        """
        sonnets = []

        try:
            with urllib.request.urlopen(POETRYDB_URL, timeout=10) as response:
                status = getattr(response, "status", None)
                if status not in (None, 200):
                    raise RuntimeError(f"Request failed with HTTP status {status}")

                try:
                    sonnets = json.load(response)
                except json.JSONDecodeError as exc:
                    raise RuntimeError(f"Failed to decode JSON: {exc}") from exc

        except (urllib.error.HTTPError,
                urllib.error.URLError,
                TimeoutError) as exc:
            raise RuntimeError(f"Network-related error occurred: {exc}") from exc

        return sonnets

    @staticmethod
    def load_sonnets() -> list[Sonnet]:
        """
        Load Shakespeare's sonnets with caching.

        Behaviour:
          1. If 'sonnets.json' already exists:
               - Print: "Loaded sonnets from cache."
               - Return the data.
          2. Otherwise:
               - Call fetch_sonnets_from_api() to load the data.
               - Print: "Downloaded sonnets from PoetryDB."
               - Save the data (pretty-printed) to CACHE_FILENAME.
               - Return the data.
        """
        sonnets_path = Paths.module_relative_path(CACHE_FILENAME)

        if os.path.exists(sonnets_path):
            try:
                with open(sonnets_path, "r", encoding="utf-8") as f:
                    try:
                        sonnets = json.load(f)
                    except json.JSONDecodeError as exc:
                        raise RuntimeError(f"Corrupt cache file (invalid JSON): {exc}") from exc
            except (OSError, IOError) as exc:
                raise RuntimeError(f"Failed to read cache file: {exc}") from exc

            print("Loaded sonnets from the cache.")
        else:
            sonnets = Loading.fetch_sonnets_from_api()
            try:
                with open(sonnets_path, "w", encoding="utf-8") as f:
                    try:
                        json.dump(sonnets, f, indent=2, ensure_ascii=False)
                    except (TypeError, ValueError) as exc:
                        raise RuntimeError(f"Failed to serialize JSON for cache: {exc}") from exc
            except (OSError, IOError) as exc:
                raise RuntimeError(f"Failed to write cache file: {exc}") from exc

            print("Downloaded sonnets from PoetryDB.")

        return [Sonnet(data) for data in sonnets]

    # ToDo 1: Moved to file_utilities.py
    @staticmethod
    def load_config() -> Configuration:
        config_file_path = Paths.module_relative_path("config.json")

        cfg = Loading.DEFAULT_CONFIG.copy()
        try:
            with open(config_file_path) as config_file:
                cfg.update(json.load(config_file))
        except FileNotFoundError:
            # File simply doesn't exist yet → quiet, just use defaults
            print("No config.json found. Using default configuration.")
            return cfg
        except json.JSONDecodeError:
            # File exists but is not valid JSON
            print("config.json is invalid. Using default configuration.")
            return cfg
        except OSError:
            # Any other OS / IO problem (permissions, disk issues, etc.)
            print("Could not read config.json. Using default configuration.")
            return cfg

        return cfg

    # ToDo 1: Moved to file_utilities.py
    @staticmethod
    def save_config(cfg: Configuration) -> None:
        config_file_path = Paths.module_relative_path("config.json")

        try:
            with open(config_file_path, "w") as config_file:
                json.dump(cfg.to_dict(), config_file, indent=4)
        except OSError:
            print(f"Writing config.json failed.")