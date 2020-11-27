import requests, bs4, time, sys, json, os

version = "1.9"
htmlFile = 'webpage.txt'
cacheFile = 'musicData.json'
linkPrefix = 'https://downloads.khinsider.com'

print("-- KHINSIDER SCRAPER --")
print(f"V. {version}\n")

def textPrompt():
    """ Read user input and return it.
    """

    response = sys.stdin.readline()
    response = response.rstrip()

    return response

def confirmationPrompt(promptText):
    """ Provide a yes/no prompt to the user.
    """

    print(f"\t:: {promptText} (y/n)")
    response = sys.stdin.readline()
    response = response.rstrip().lower()

    if response == 'y':
        return True

    return False

def statusMessage(message, status=None, prefix="  ", suffix=""):
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

    statusMessage("Scraping list of tracks from site...", status="scraper:hrefs")
    trackList = []
    for item in selection:
        link = item.get('href')
        musicTitle = item.parent.parent.find('td', class_="clickable-row").a.string

        track = {
            'title': musicTitle.replace(' ', '_'),
            'link': f'{linkPrefix}{link}',
        }
        trackList.append(track)
    statusMessage(f"Found {len(trackList)} tracks.", status="scraper:hrefs")

    return trackList

def scrapeSongLinks(trackList):
    """ Scrape a list of track links from the site.
    """

    musicList = []
    trackCount = len(trackList)
    count = 1
    sleepTimer = 25 if trackCount < 26 else 15

    timeOfArrival = (sleepTimer * trackCount) / 60
    statusMessage(f"Fetching download links in {sleepTimer} second intervals.", status="scraper:links")
    statusMessage(f"This is estimated to take {round(timeOfArrival, 2)} minutes.\n", status="scraper:links")

    for track in trackList:
        statusMessage(f"TRACK {count} OF {trackCount}...", prefix="")

        res = requests.get(track['link'])
        type(res)
        res.raise_for_status()

        parsedHtml = bs4.BeautifulSoup(res.text, features="html.parser")
        selection = parsedHtml.find('span', class_="songDownloadLink")
        music = {
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

def downloadTracks(musicList):
    """ Download a list of links
    """

    trackCount = len(musicList)
    count = 1
    sleepTimer = 10
    statusMessage("Starting...", status="download", prefix="\n", suffix="\n")

    for music in musicList:
        statusMessage(f"({count} OF {trackCount}) | '{music['title']}'", prefix="")

        download = requests.get(music['link'])
        type(download)
        download.raise_for_status()

        with open(f"./downloadedTracks/{music['title']}.mp3", 'wb') as musicFile:
            musicFile.write(download.content)

        if count != trackCount:
            time.sleep(sleepTimer)
        count += 1

    statusMessage("Complete!", status="download")
    cleanDir()

def main():
    if os.path.isfile(cacheFile) and confirmationPrompt("Found a cache file, download it?"):
        with open(cacheFile, 'r') as cache:
            musicList = json.load(cache)
        downloadTracks(musicList)
    else:
        print("Paste link to download from khinsider: ")
        link = textPrompt()
        downloadWebpage(link)
        html = parseHtml()
        trackList = scrapeHrefs(html)
        musicList = scrapeSongLinks(trackList)

        if confirmationPrompt("Download music now?"):
            downloadTracks(musicList)

    statusMessage("Finished!", status="khscraper")

main()
