import requests, bs4, time, sys

htmlFile = 'webpage.txt'
prefix = 'https://downloads.khinsider.com'

print("-- KHINSIDER SCRAPER --")
print("V. 1.3\n")

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

def downloadWebpage(link):
    print("[download] Fetching webpage...")
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

    print('[scraper] Scraping list of links from site...')
    trackList = []
    for item in selection:
        link = item.get('href')
        musicTitle = item.parent.parent.find('td', class_="clickable-row").a.string

        track = {
            'title' : musicTitle.replace(' ', '_'),
            'link': '{}{}'.format(prefix, link),
        }
        trackList.append(track)
    print('[scraper] Found {} tracks.'.format(len(trackList)))

    return trackList

def downloadTrack(link, title):
    download = requests.get(link)
    type(download)

    download.raise_for_status()

    with open('./downloadedTracks/{}.mp3'.format(title), 'wb') as musicFile:
        musicFile.write(download.content)
    print(' Done!')

def scrapeSongLinks(trackList):
    trackCount = len(trackList)
    count = 1
    downloadAlong = False
    sleepTimer = 20 if trackCount < 26 else 15

    if confirmationPrompt('\nDo you wish to download the tracks alongside?'):
        downloadAlong = True
        sleepTimer = 10

    timeOfArrival = (sleepTimer * trackCount) / 60
    print('\n[i] Grabbing download links in {} second intervals.'.format(sleepTimer))
    print('[i] This is estimated to take {} minutes\n'.format(round(timeOfArrival, 2)))

    with open('./downloadedTracks/linkData.txt', 'w') as linkData:
        for track in trackList:
            res = requests.get(track['link'])
            type(res)

            res.raise_for_status()

            parsedHtml = bs4.BeautifulSoup(res.text, features="html.parser")
            selection = parsedHtml.find('span', class_="songDownloadLink")

            link = selection.parent['href']
            musicTitle = track['title']

            linkData.write('{} -o {}.mp3\n'.format(link, musicTitle))

            print(' TRACK {} OF {}'.format(count, trackCount))
            print(' TITLE : {}'.format(musicTitle))
            if downloadAlong:
                print(' Downloading...', end='')
                downloadTrack(link, musicTitle)
            print('---------------')

            if count != trackCount:
                time.sleep(sleepTimer)
            count += 1

def main():
    print("Paste link to download from khinsider: ")
    link = textPrompt()
    downloadWebpage(link)
    html = parseHtml()
    trackList = scrapeHrefs(html)

    if confirmationPrompt("Do you wish to start fetching links now?"):
        scrapeSongLinks(trackList)
    else:
        print("[i] Aborted by user.")

    print('\n[khscraper] Finished!')

main()
