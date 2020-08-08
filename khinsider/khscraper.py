import requests, bs4, time, sys, json, os

htmlFile = 'webpage.txt'
cacheFile = 'musicData.json'
prefix = 'https://downloads.khinsider.com'

print("-- KHINSIDER SCRAPER --")
print("V. 1.7\n")

def textPrompt():
    text = sys.stdin.readline()
    text = text.rstrip()

    return text

def confirmationPrompt(promptText):
    print(promptText + " (y/n)")
    text = sys.stdin.readline()
    text = text.rstrip().lower()

    if text == 'y':
        return True

    return False

def cleanDir():
    if os.path.isfile(htmlFile):
        os.remove(htmlFile)
    if os.path.isfile(cacheFile):
        os.remove(cacheFile)

def downloadWebpage(link):
    print("[download] Downloading webpage...")
    response = requests.get(link)
    type(response)
    response.raise_for_status()

    with open(htmlFile, 'wb') as saveFile:
        for chunk in response.iter_content(100000):
            saveFile.write(chunk)

def parseHtml():
    with open(htmlFile) as rawHtml:
        parsedHtml = bs4.BeautifulSoup(rawHtml.read(), features="html.parser")

    return parsedHtml

def scrapeHrefs(parsedHtml):
    selection = parsedHtml.select('.playlistDownloadSong a')
    type(selection)

    print('[scraper] Scraping list of tracks from site...')
    trackList = []
    for item in selection:
        link = item.get('href')
        musicTitle = item.parent.parent.find('td', class_="clickable-row").a.string

        track = {
            'title': musicTitle.replace(' ', '_'),
            'link': '{}{}'.format(prefix, link),
        }
        trackList.append(track)
    print('[scraper] Found {} tracks.'.format(len(trackList)))

    return trackList

def scrapeSongLinks(trackList):
    musicList = []
    trackCount = len(trackList)
    count = 1
    sleepTimer = 25 if trackCount < 26 else 15

    timeOfArrival = (sleepTimer * trackCount) / 60
    print('[scraper] Grabbing download links in {} second intervals.'.format(sleepTimer))
    print('[scraper] This is estimated to take {} minutes\n'.format(round(timeOfArrival, 2)))

    for track in trackList:
        print(' TRACK {} OF {}...'.format(count, trackCount))

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
    trackCount = len(musicList)
    count = 1
    sleepTimer = 10
    print('\n[download] Starting...\n')

    for music in musicList:
        print(' ({} OF {}) | "{}"'.format(count, trackCount, music['title']))

        download = requests.get(music['link'])
        type(download)
        download.raise_for_status()

        with open('./downloadedTracks/{}.mp3'.format(music['title']), 'wb') as musicFile:
            musicFile.write(download.content)

        if count != trackCount:
            time.sleep(sleepTimer)
        count += 1

    print('[download] Complete!')
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

        if confirmationPrompt("\nDownload music now?"):
            downloadTracks(musicList)

    print('[khscraper] Finished!')

main()
