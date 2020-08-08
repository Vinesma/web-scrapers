import requests, bs4, time, sys

htmlFile = 'webpage.txt'
prefix = 'https://downloads.khinsider.com'

print("-- KHINSIDER SCRAPER --")
print("V. 1.1\n")

def handleText():
    text = sys.stdin.readline()
    text = text.rstrip()

    return text

def downloadWebpage(link):
    print("[download] Fetching webpage...")
    response = requests.get(link)
    type(response)

    # Raises an exception if the download is unsuccessful
    response.raise_for_status()

    saveFile = open(htmlFile, 'wb')
    for chunk in response.iter_content(100000):
        saveFile.write(chunk)
    saveFile.close()

def parseHtml():
    rawHtml = open(htmlFile)
    parsedHtml = bs4.BeautifulSoup(rawHtml.read(), features="html.parser")
    rawHtml.close()

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

def scrapeSongLinks(trackList):
    trackCount = len(trackList)
    count = 1
    sleepTimer = 20 if trackCount < 26 else 15
    timeOfArrival = (sleepTimer * trackCount) / 60

    print('\n[i] Grabbing download links in {} second intervals.'.format(sleepTimer))
    print('[i] This is estimated to take {} minutes\n'.format(round(timeOfArrival, 2)))
    
    linkData = open('./downloadedTracks/linkData.txt', 'w')
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
        print('---------------')
        if count != trackCount:
            time.sleep(sleepTimer)
        count += 1

    linkData.close()

def main():
    print("Paste link to download from khinsider: ")
    link = handleText()
    downloadWebpage(link)
    html = parseHtml()
    trackList = scrapeHrefs(html)
    scrapeSongLinks(trackList)
    
    print('\n[khscraper] Finished!')

main()
