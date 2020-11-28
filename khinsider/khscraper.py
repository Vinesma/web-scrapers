import requests, bs4, time, sys, json, os

version = "2.4"
htmlFile = 'webpage.txt'
cacheFile = 'music_data.json'
linkPrefix = 'https://downloads.khinsider.com'
supportedLinkPrefix = 'https://downloads.khinsider.com/game-soundtracks/album/'

print("-- KHINSIDER SCRAPER --")
print(f"V. {version}\n")

def clearScreen():
    """ Clears the terminal screen using the OS specific method.
    """
    os.system('clear' if sys.platform == 'linux' else 'cls')

def isSupported(link):
    """ Verify if the provided link is supported
    """
    if link.startswith(supportedLinkPrefix):
        return True

    return False

def foundCache():
    """ Determine if a cache file exists
    """
    if os.path.isfile(cacheFile) and confirmationPrompt("Found a cache file, download it?"):
        return True

    return False

def textPrompt():
    """ Read user input and return it.
    """
    response = sys.stdin.readline()
    response = response.rstrip()

    return response

def confirmationPrompt(promptText):
    """ Provide a yes/no prompt to the user.
    """
    print(f":: {promptText} (y/n)")
    response = sys.stdin.readline()
    response = response.rstrip().lower()

    if response == 'y':
        return True

    return False

def statusMessage(message, status=None, prefix="", suffix=""):
    """ Show a status message to the user, the current action is represented in brackets.
    """
    if status is not None:
        print(f"{prefix}[{status}] {message}{suffix}")
    else:
        print(f"{prefix}{message}{suffix}")

def cleanDir():
    """ Clean the directory of all temporary files.
    """
    if os.path.isfile(htmlFile):
        os.remove(htmlFile)
    if os.path.isfile(cacheFile):
        os.remove(cacheFile)

    statusMessage("Directory cleaned!", status="clean")

def downloadWebpage(link):
    """ Download and save a webpage as html.
    """
    statusMessage("Downloading webpage...", status="download:webpage", prefix="\n")
    response = requests.get(link)
    type(response)
    response.raise_for_status()

    with open(htmlFile, 'wb') as saveFile:
        for chunk in response.iter_content(100000):
            saveFile.write(chunk)

def parseHtml():
    """ Read a saved html file and return a parsed object.
    """
    with open(htmlFile) as rawHtml:
        parsedHtml = bs4.BeautifulSoup(rawHtml.read(), features="html.parser")

    return parsedHtml

def scrapeHrefs(parsedHtml):
    """ Scrape a list of all tracks from the site.
    """
    selection = parsedHtml.select('.playlistDownloadSong a')
    type(selection)

    statusMessage("Scraping list of tracks from site...", status="scraper:tracks")
    trackList = []
    for item in selection:
        link = item.get('href')
        musicTitle = item.parent.parent.find('td', class_="clickable-row").a.string

        track = {
            'title': musicTitle.replace(' ', '_'),
            'link': f'{linkPrefix}{link}',
        }
        trackList.append(track)
    statusMessage(f"Found {len(trackList)} tracks.", status="scraper:tracks")

    return trackList

def scrapeSongLinks(trackList):
    """ Scrape a list of track links from the site.
    """
    musicList = []
    trackCount = len(trackList)
    count = 1
    sleepTimer = 25 if trackCount < 26 else 15

    timeOfArrival = (sleepTimer * trackCount) / 60
    statusMessage(f"Fetching download links in {sleepTimer} second intervals.", status="scraper:hrefs")
    statusMessage(f"This is estimated to take {round(timeOfArrival, 2)} minutes.", status="scraper:hrefs", suffix="\n")

    for track in trackList:
        statusMessage(f"TRACK {count:03d} OF {trackCount}...", prefix="")

        res = requests.get(track['link'])
        type(res)
        res.raise_for_status()

        parsedHtml = bs4.BeautifulSoup(res.text, features="html.parser")
        selection = parsedHtml.find('span', class_="songDownloadLink")
        music = {
            'picked': True,
            'link': selection.parent['href'],
            'title': track['title'],
        }
        musicList.append(music)

        if count != trackCount:
            time.sleep(sleepTimer)
        count += 1

    with open(cacheFile, 'w') as musicData:
        musicData.write(json.dumps(musicList))

    return musicList

def listTracks(musicList):
    """ Print tracks from a list
    """
    clearScreen()
    for i, track in enumerate(musicList, start=1):
        selection = 'x' if track['picked'] else ' '
        print(f"[{selection}] {i} : {track['title']}")

def chooser(musicList):
    """ Exclude/Include tracks for download
    """
    print("Enter a comma separated list of numbers to exclude/include. Eg. (1,5,8,17)")
    print("Items included will be excluded, items excluded will be included.")
    choices = textPrompt().split(',')
    clearScreen()

    for item in choices:
        try:
            itemNumber = int(item)
            isPicked = musicList[itemNumber - 1]['picked']
            trackName = musicList[itemNumber - 1]['title']

            selection = 'x' if not isPicked else ' '
            musicList[itemNumber - 1]['picked'] = not isPicked

            print(f"[{selection}] : {trackName}")
        except (IndexError, ValueError):
            pass

    return musicList

def trackPicker(musicList):
    """ Displays a dialog allowing the user to choose what to download.
    """
    clearScreen()
    userIsNotDone = True

    while userIsNotDone:
        print("\n:: Music Picker ::")
        print("1) List tracks")
        print("2) Exclude/Include tracks for download")
        print("3) Select All")
        print("4) Deselect All")
        print("5) Done!")

        print("What to do?")
        response = textPrompt()
        if response == '1':
            listTracks(musicList)
        elif response == '2':
            musicList = chooser(musicList)
        elif response == '3':
            for item in musicList:
                item['picked'] = True
            listTracks(musicList)
        elif response == '4':
            for item in musicList:
                item['picked'] = False
            listTracks(musicList)
        elif response == '5':
            if confirmationPrompt("Are you sure?"):
                userIsNotDone = False
            clearScreen()
        else:
            print("Invalid option, try again.")

    return musicList

def downloadTracks(musicList):
    """ Download a list of links.
    """
    trackCount = len(musicList)

    sleepTimer = 10
    downloadHappened = False
    statusMessage("Starting...", status="download", prefix="\n", suffix="\n")

    for i, music in enumerate(musicList, start=1):
        if music['picked']:
            statusMessage(f"({i:03d} OF {trackCount}) | '{music['title']}'", prefix="")
            download = requests.get(music['link'])
            type(download)
            download.raise_for_status()

            with open(f"./downloadedTracks/{music['title']}.mp3", 'wb') as musicFile:
                musicFile.write(download.content)
            downloadHappened = True

            # Skip last item's sleep
            if i != trackCount:
                time.sleep(sleepTimer)

    if downloadHappened:
        statusMessage("Complete!", status="download", prefix="\n")
        cleanDir()
    else:
        if confirmationPrompt("Nothing has been downloaded, was this in error?"):
            statusMessage("Understood, your cache was preserved.")
        else:
            statusMessage("Understood, cleaning house.")
            cleanDir()

def downloadFromCache():
    """ Loads json information from cache, then downloads it.
    """
    # Load music list from json cache
    with open(cacheFile, 'r') as cache:
        musicList = json.load(cache)

    if confirmationPrompt("Show track chooser?"):
        musicList = trackPicker(musicList)

    downloadTracks(musicList)

def downloadFromLink():
    """ Receive a link, download the webpage, list all the music and download it if the user wants.
    """
    print("Paste link to download from khinsider: ")
    link = textPrompt()
    if isSupported(link):
        downloadWebpage(link)
        html = parseHtml()
        trackList = scrapeHrefs(html)
        musicList = scrapeSongLinks(trackList)

        if confirmationPrompt("Show track chooser?"):
            musicList = trackPicker(musicList)

        if confirmationPrompt("Download music now?"):
            downloadTracks(musicList)
    else:
        print("Err: This link is not supported.")

def main():
    try:
        if foundCache():
            downloadFromCache()
        else:
            downloadFromLink()
        statusMessage("Finished!", status="khscraper")
    except KeyboardInterrupt:
        sys.exit("Interrupted by user.")

main()
