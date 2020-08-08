import requests, bs4, time, sys, json, os

htmlFile = 'webpage.txt'
prefix = 'https://downloads.khinsider.com'

print("-- KHINSIDER SCRAPER --")
print("V. 1.5\n")

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

def fileExists(filename):
    if os.path.isfile(filename):
        return True

    return False

def cleanDir():
    if fileExists(htmlFile):
        os.remove(htmlFile)
    if fileExists('musicData.json'):
        os.remove('musicData.json')
    print("\n[i] Cleanup complete!")

def downloadWebpage(link):
    print("[page] Downloading webpage...")
    response = requests.get(link)
    type(response)

    # Raises an exception if the download is unsuccessful
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
    print('\n[link-scraper] Grabbing download links in {} second intervals.'.format(sleepTimer))
    print('[link-scraper] This is estimated to take {} minutes\n'.format(round(timeOfArrival, 2)))

    for track in trackList:
        res = requests.get(track['link'])
        type(res)

        print(' TRACK {} OF {}...'.format(count, trackCount), end='')

        res.raise_for_status()

        parsedHtml = bs4.BeautifulSoup(res.text, features="html.parser")
        selection = parsedHtml.find('span', class_="songDownloadLink")
        music = {
            'link': selection.parent['href'],
            'title': track['title'],
        }
        musicList.append(music)
        print(' Done.')

        if count != trackCount:
            time.sleep(sleepTimer)
        count += 1

    with open('musicData.json', 'w') as musicData:
        musicData.write(json.dumps(musicList))

    return musicList

def downloadTracks(musicList):
    trackCount = len(musicList)
    count = 1
    sleepTimer = 10
    print('\n[music] Download starting...\n')

    for music in musicList:
        download = requests.get(music['link'])
        type(download)

        print(' TRACK {} OF {}...'.format(count, trackCount))
        print(' DOWNLOADING: {}'.format(music['title']), end='')

        download.raise_for_status()

        with open('./downloadedTracks/{}.mp3'.format(music['title']), 'wb') as musicFile:
            musicFile.write(download.content)
        print(' Done.')
        print('------------------')

        if count != trackCount:
            time.sleep(sleepTimer)
        count += 1

    print('[music] Download complete!')
    cleanDir()

def main():
    if fileExists('musicData.json') and confirmationPrompt("Found a cache file, download it?"):
        with open('musicData.json', 'r') as jsonCache:
            musicList = json.load(jsonCache)
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

    print('\n[khscraper] Finished!')

main()
