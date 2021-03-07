""" 
Scrape, view and download music from khinsider.
"""
import os
import argparse
import json
import sys
import time
from random import randrange

import requests
import bs4

from utils import messages, page

# GLOBALS
version = "3.1"
url = ""
quick_download = False
linkPrefix = "https://downloads.khinsider.com"
supported_link_prefix = "https://downloads.khinsider.com/game-soundtracks/album/"
# PATHS
cache_path = os.path.join(".", "cache")
download_path = os.path.join(".", "files", "downloaded_files")
raw_html = os.path.join(cache_path, "webpage.txt")
cache_file = os.path.join(cache_path, "music_data.json")
to_clean = [ raw_html, cache_file ]

print("-- KHINSIDER SCRAPER --")
print(f"V. {version}\n")

def load_args():
    """ 
    Parse and load arguments
    """
    global url
    global quick_download

    # Initializer
    parser = argparse.ArgumentParser(description="Scrape, view and download music from khscraper.")
    # Argument definition
    # optional
    parser.add_argument("-q", "--quickdown", help="skip asking and download straightaway after scraping is done. This also skips file selection.", action="store_true")
    #TODO parser.add_argument("-v", "--verbose", help="make the application more verbose.", action="store_true")
    # positional
    parser.add_argument("url", help="URL to the album page")
    args = parser.parse_args()

    if args.quickdown:
        quick_download = True

    url = args.url

def clear_screen():
    """ 
    Clears the terminal screen using the OS specific method.
    """
    os.system('clear' if sys.platform == 'linux' else 'cls')

def is_supported(link):
    """ 
    Verify if the provided link is supported
    """
    if link.startswith(supported_link_prefix):
        return True

    return False

def found_cache():
    """ 
    Determine if a cache file exists
    """
    if os.path.isfile(cache_file) and messages.question_bool("Found a cache file, download it?"):
        return True

    return False

def clean():
    """ 
    Clean the directory of all temporary files.
    """
    for file_ in to_clean:
        if os.path.isfile(file_):
            os.remove(file_)

    messages.status("Directory cleaned!", status="clean")

def scrape_hrefs(parsed_html):
    """ 
    Scrape a list of all tracks from the site.
    """
    selection = parsed_html.select('.playlistDownloadSong a')
    type(selection)

    messages.status("Scraping list of tracks from site...", status="scraper:tracks")
    tracks = []
    for item in selection:
        link = item.get('href')
        music_title = item.parent.parent.find('td', class_="clickable-row").a.string

        track = {
            'title': music_title.replace(' ', '_'),
            'link': f'{linkPrefix}{link}',
        }
        tracks.append(track)
    messages.status(f"Found {len(tracks)} tracks.", status="scraper:tracks")

    return tracks

def scrape_song_links(tracks):
    """ 
    Scrape a list of track links from the site.
    """
    music_list = []
    track_count = len(tracks)
    count = 1
    sleep_timer = 16 if track_count < 26 else 12

    time_of_arrival = (sleep_timer * track_count) / 60
    messages.status(f"Fetching download links in ~{sleep_timer} second intervals.", status="scraper:hrefs")
    messages.status(f"This is estimated to take {round(time_of_arrival, 2)} minutes.", status="scraper:hrefs", suffix="\n")

    for track in tracks:
        messages.status(f"TRACK {count:03d} of {track_count}...", prefix="")

        response = page.download(track["link"])

        parsed_html = bs4.BeautifulSoup(response.text, features="html.parser")
        selection = parsed_html.find("span", class_="songDownloadLink")
        music = {
            "picked": True,
            "link": selection.parent["href"],
            "title": track["title"],
        }
        music_list.append(music)

        if count != track_count:
            time.sleep(randrange(8, sleep_timer))
        count += 1

    with open(cache_file, "w") as music_data:
        music_data.write(json.dumps(music_list))

    return music_list

def list_tracks(music_list):
    """ 
    Print tracks from a list
    """
    clear_screen()
    for i, track in enumerate(music_list, start=1):
        selection = "x" if track["picked"] else " "
        print(f"[{selection}] {i} : {track['title']}")

def chooser(music_list):
    """ 
    Exclude/Include tracks for download
    """
    print("Enter a comma separated list of numbers to exclude/include. Eg. (1,5,8,17)")
    print("Items included will be excluded, items excluded will be included.")
    choices = messages.question_str("").split(',')
    clear_screen()

    for item in choices:
        try:
            item_number = int(item)
            is_picked = music_list[item_number - 1]["picked"]
            track_name = music_list[item_number - 1]["title"]

            selection = "x" if not is_picked else " "
            music_list[item_number - 1]["picked"] = not is_picked

            print(f"[{selection}] : {track_name}")
        except (IndexError, ValueError):
            pass

    return music_list

def track_picker(music_list):
    """ 
    Displays a dialog allowing the user to choose what to download.
    """
    clear_screen()
    user_not_done = True

    while user_not_done:
        print("\n:: Music Picker ::")
        print("1) List tracks")
        print("2) Exclude/Include tracks for download")
        print("3) Select All")
        print("4) Deselect All")
        print("5) Done!")

        print("What to do?")
        response = messages.question_str("")
        if response == "1":
            list_tracks(music_list)
        elif response == "2":
            music_list = chooser(music_list)
        elif response == "3":
            for item in music_list:
                item["picked"] = True
            list_tracks(music_list)
        elif response == "4":
            for item in music_list:
                item["picked"] = False
            list_tracks(music_list)
        elif response == "5":
            if messages.question_bool("Are you sure?"):
                user_not_done = False
            clear_screen()
        else:
            print("Invalid option, try again.")

    return music_list

def download_tracks(music_list):
    """ 
    Download a list of links.
    """
    track_count = len(music_list)

    sleep_timer = 10
    download_happened = False
    messages.status("Starting...", status="download", prefix="\n", suffix="\n")

    for i, music in enumerate(music_list, start=1):
        if music['picked']:
            messages.status(f"({i:03d} of {track_count}) | '{music['title']}'", prefix="")
            download = page.download(music["link"])

            if not os.path.isdir(download_path):
                os.makedirs(download_path)

            with open(os.path.join(download_path, f"{music['title']}.mp3"), "wb") as musicFile:
                musicFile.write(download.content)
            download_happened = True

            # Skip last item's sleep
            if i != track_count:
                time.sleep(randrange(5, sleep_timer))

    if download_happened:
        messages.status("Complete!", status="download", prefix="\n")
        clean()
    else:
        if messages.question_bool("Nothing has been downloaded, was this in error?"):
            messages.status("Understood, your cache was preserved.")
        else:
            messages.status("Understood, cleaning house.")
            clean()

def download_from_cache():
    """ 
    Loads json information from cache, then downloads it.
    """
    # Load music list from json cache
    with open(cache_file, 'r') as cache:
        music_list = json.load(cache)

    if not quick_download and messages.question_bool("Show track chooser?"):
        music_list = track_picker(music_list)

    download_tracks(music_list)

def download_from_url(link):
    """
    Receive a link, download the webpage, list all the music and download it if the user wants.
    """
    if is_supported(link):
        page.download_save(link, raw_html)
        html = page.parse(raw_html)
        tracks = scrape_hrefs(html)
        music_list = scrape_song_links(tracks)

        if not quick_download:
            if messages.question_bool("Show track chooser?"):
                music_list = track_picker(music_list)

            if messages.question_bool("Download music now?"):
                download_tracks(music_list)
        else:
            download_tracks(music_list)
    else:
        print("Err: This link is not supported.")

def main():
    load_args()
    try:
        if found_cache():
            download_from_cache()
        else:
            download_from_url(url)
        messages.status("Finished!", status="khscraper")
    except KeyboardInterrupt:
        sys.exit("Interrupted by user.")

if __name__ == "__main__":
    main()