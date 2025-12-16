#!/usr/bin/env python3
"""
Part 9 starter CLI.

WHAT'S NEW IN PART 9
Our very first new module! And... we are finally again adding new functionality.
"""

# ToDo 1: You will need to move and change some imports
from typing import List
import time


from constants import BANNER, HELP
from file_utilities import Loading, Printing






def main() -> None:
    print(BANNER)
    # ToDo 1: Depending on how your imports look, you may need to adapt the call to load_config()
    config = Loading.load_config()

    # Load sonnets (from cache or API)
    start = time.perf_counter()
    # ToDo 1: Depending on how your imports look, you may need to adapt the call to load_sonnets()
    sonnets = Loading.load_sonnets()

    elapsed = (time.perf_counter() - start) * 1000
    print(f"Loading sonnets took: {elapsed:.3f} [ms]")

    print(f"Loaded {len(sonnets)} sonnets.")

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not raw:
            continue

        # commands
        if raw.startswith(":"):
            if raw == ":quit":
                print("Bye.")
                break

            if raw == ":help":
                print(HELP)
                continue

            if raw.startswith(":highlight"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].lower() in ("on", "off"):
                    config.highlight = parts[1].lower() == "on"
                    print("Highlighting", "ON" if config.highlight else "OFF")
                    # ToDo 1: Depending on how your imports look, you may need to adapt the call to save_config()
                    # ToDo 3: You need to adapt the call to save_config
                    Loading.save_config(config)
                else:
                    print("Usage: :highlight on|off")
                continue

            if raw.startswith(":search-mode"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].upper() in ("AND", "OR"):
                    config.search_mode = parts[1].upper()
                    print("Search mode set to", config.search_mode)
                    # ToDo 3: You need to adapt the call to save_config
                    Loading.save_config(config)
                else:
                    print("Usage: :search-mode AND|OR")
                continue

            # ToDo 2: A new setting is added here. It's command string is ':hl-mode'.
            if raw.startswith(":hl-mode"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].upper() in ("DEFAULT", "GREEN"):
                    config.hl_mode = parts[1].upper()
                    print("Highlighting mode set to", config.hl_mode)
                    Loading.save_config(config)
                else:
                    print("Usage: :highlight-mode DEFAULT|GREEN")
                continue
            print("Unknown command. Type :help for commands.")
            continue

        # ---------- Query evaluation ----------
        words = raw.split()
        if not words:
            continue

        start = time.perf_counter()

        # query
        combined_results = []

        words = raw.split()

        for word in words:
            # Searching for the word in all sonnets
            # ToDo 0:You will need to adapt the call to search_sonnet
            results = [s.search_for(word) for s in sonnets]

            if not combined_results:
                # No results yet. We store the first list of results in combined_results
                combined_results = results
            else:
                # We have an additional result, we have to merge the two results: loop all sonnets
                for i in range(len(combined_results)):
                    # Checking each sonnet individually
                    combined_result = combined_results[i]
                    result = results[i]

                    if config.search_mode == "AND":
                        if combined_result.matches > 0 and result.matches > 0:
                            # Only if we have matches in both results, we consider the sonnet (logical AND!)
                            # ToDo 0:You will need to adapt the call to combine_results
                            combined_results[i] = combined_result.combine_results(result)
                        else:
                            # Not in both. No match!
                            combined_result.matches = 0
                    elif config.search_mode == "OR":
                        # ToDo 0:You will need to adapt the call to combine_results
                        combined_results[i] = combined_result.combine_results(result)

        # Initialize elapsed_ms to contain the number of milliseconds the query evaluation took
        elapsed_ms = (time.perf_counter() - start) * 1000

        # ToDo 2: You will need to pass the new setting, the highlight_mode to print_results and use it there

        Printing.print_results(raw, combined_results, highlight=config.highlight, hl_mode= config.hl_mode, query_time_ms=elapsed_ms)


if __name__ == "__main__":
    main()
