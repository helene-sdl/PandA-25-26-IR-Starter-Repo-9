# ToDo 1: Move to file_utilities.py
import json
import os
import urllib.request
import urllib.error
from constants import POETRYDB_URL, CACHE_FILENAME
from models import Sonnet, SearchResult
from typing import List, Dict, Any
#move module_relative_path to load/save config and move load/save config to configuration!!
class Configuration:
    #added hl mode
    """
        A small configuration container for user preferences in the IR system.
        Stores two settings:
          - highlight: whether matches should be highlighted using ANSI colors.
          - search_mode: logical mode for combining multiple search terms ("AND" or "OR").
    """
    def __init__(self):
        # Default settings used at program startup.
        self.highlight = True
        self.search_mode = "AND"
        self.hl_mode = "DEFAULT"

    def copy(self):
        """
            Return a *shallow copy* of this configuration object.
            Useful when you want to pass config around without mutating the original.
        """
        copy = Configuration()
        copy.highlight = self.highlight
        copy.search_mode = self.search_mode
        copy.hl_mode = self.hl_mode
        return copy

    def update(self, other: Dict[str, Any]):
        """
            Update this configuration using values from a (loaded) dictionary.
            Only accepts valid keys and types:
              - "highlight": must be a boolean
              - "search_mode": must be "AND" or "OR"

            Invalid entries are silently ignored, ensuring robustness
            against corrupted or manually edited config files.
        """
        if "highlight" in other and isinstance(other["highlight"], bool):
            self.highlight = other["highlight"]

        if "search_mode" in other and other["search_mode"] in ["AND", "OR"]:
            self.search_mode = other["search_mode"]
        #add highlight options
        if "hl_mode" in other and other["hl_mode"] in ["DEFAULT", "GREEN"]:
            self.hl_mode = other["hl_mode"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "highlight": self.highlight,
            "search_mode": self.search_mode,
            "hl_mode": self.hl_mode,
        }
        # ToDo 1: Moved to file_utilities.py

    @staticmethod
    def load() -> "Configuration":
        config_file_path = Paths.module_relative_path("config.json")

        cfg = Loader.DEFAULT_CONFIG.copy()
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
    def save(self) -> None:
        config_file_path = Paths.module_relative_path("config.json")

        try:
            with open(config_file_path, "w") as config_file:
                json.dump(self.to_dict(), config_file, indent=4)
        except OSError:
            print(f"Writing config.json failed.")

#created class printing in file_utilities
class Printer:
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
            title_line = (
                # ToDo 2: You will need to pass the new setting, the highlight_mode to ansi_highlight and use it there
                r.ansi_highlight(r.title, r.title_spans, mode=hl_mode)
                if highlight
                else r.title
            )
            print(f"\n[{idx}/{total_docs}] {title_line}")
            for lm in r.line_matches:
                line_out = (
                    # ToDo 2: You will need to pass the new setting, the highlight_mode to ansi_highlight and use it there
                    r.ansi_highlight(lm.text, lm.spans, mode=hl_mode)
                    if highlight
                    else lm.text
                )
                print(f"  [{lm.line_no:2}] {line_out}")


class Paths:
    @staticmethod
    def module_relative_path(name: str) -> str:
        """Return absolute path for a file next to this module."""
        return os.path.join(os.path.dirname(__file__), name)

# ToDo 1: Move to file_utilities.py
class Loader:

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
    def load_sonnets() -> List[Sonnet]:
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
            sonnets = Loader.fetch_sonnets_from_api()
            try:
                with open(sonnets_path, "w", encoding="utf-8") as f:
                    try:
                        json.dump(sonnets, f, indent=2, ensure_ascii=False)
                    except (TypeError, ValueError) as exc:
                        raise RuntimeError(f"Failed to serialize JSON for cache: {exc}") from exc
            except (OSError, IOError) as exc:
                raise RuntimeError(f"Failed to write cache file: {exc}") from exc

            print("Downloaded sonnets from PoetryDB.")

        if not all(isinstance(d, dict) for d in sonnets):
            raise RuntimeError("Sonnets data is invalid after decoding")

        return [Sonnet(data) for data in sonnets]
