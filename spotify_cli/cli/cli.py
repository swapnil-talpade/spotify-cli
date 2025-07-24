"""CLI module for the Spotify CLI Player"""

import argparse
import os
import readline
from ..controllers.spotify_controller import SpotifyController


def main():
    parser = argparse.ArgumentParser(description="Spotify CLI Player")
    parser.add_argument(
        "command",
        nargs="?",
        choices=[
            "play",
            "quickplay",
            "pause",
            "resume",
            "next",
            "prev",
            "current",
            "devices",
            "volume",
        ],
        help="Command to execute",
    )
    parser.add_argument(
        "query", nargs="*", help="Search query for play command or volume level"
    )

    args = parser.parse_args()

    # Initialize Spotify controller
    try:
        spotify = SpotifyController()
    except SystemExit:
        return

    histfile = os.path.join(os.path.expanduser("~"), ".spotify_cli_history")
    try:
        readline.read_history_file(histfile)
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass

    if not args.command:
        # Interactive mode
        print("🎵 Spotify CLI Player")
        print(
            "Commands: play <song>, quickplay <song>, pause, resume, next, prev, current, devices, volume <level>, quit"
        )

        while True:
            try:
                cmd = input("\n🎵 > ").strip().split()
                if not cmd:
                    continue

                command = cmd[0].lower()

                if command in ["quit", "exit", "q"]:
                    readline.write_history_file(histfile)
                    print("👋 Goodbye!")
                    break
                elif command == "play" and len(cmd) > 1:
                    query = " ".join(cmd[1:])
                    spotify.search_and_play(query)
                elif command == "quickplay" and len(cmd) > 1:
                    query = " ".join(cmd[1:])
                    enhanced_query = spotify.enhance_search_query(query)
                    if enhanced_query != query:
                        print(f"🤖 Enhanced search: '{enhanced_query}'")
                    spotify.play_best_match(enhanced_query)
                elif command == "pause":
                    spotify.pause()
                elif command == "resume":
                    spotify.resume()
                elif command == "next":
                    spotify.next_track()
                elif command == "prev":
                    spotify.previous_track()
                elif command == "current":
                    spotify.current_track()
                elif command == "devices":
                    spotify.show_devices()
                elif command == "volume" and len(cmd) > 1:
                    try:
                        vol = int(cmd[1])
                        spotify.set_volume(vol)
                    except ValueError:
                        print("❌ Invalid volume level")
                else:
                    print("❌ Unknown command or missing arguments")

            except KeyboardInterrupt:
                readline.write_history_file(histfile)  # Save history on interrupt
                print("\n👋 Goodbye!")
                break
    else:
        # Command line mode
        if args.command == "play":
            if args.query:
                query = " ".join(args.query)
                spotify.search_and_play(query)
            else:
                print("❌ Please provide a search query")
        elif args.command == "quickplay":
            if args.query:
                query = " ".join(args.query)
                enhanced_query = spotify.enhance_search_query(query)
                if enhanced_query != query:
                    print(f"🤖 Enhanced search: '{enhanced_query}'")
                spotify.play_best_match(enhanced_query)
            else:
                print("❌ Please provide a search query")
        elif args.command == "pause":
            spotify.pause()
        elif args.command == "resume":
            spotify.resume()
        elif args.command == "next":
            spotify.next_track()
        elif args.command == "prev":
            spotify.previous_track()
        elif args.command == "current":
            spotify.current_track()
        elif args.command == "devices":
            spotify.show_devices()
        elif args.command == "volume":
            if args.query:
                try:
                    vol = int(args.query[0])
                    spotify.set_volume(vol)
                except ValueError:
                    print("❌ Invalid volume level")
            else:
                print("❌ Please provide a volume level (0-100)")


if __name__ == "__main__":
    main()
