import requests, bs4, time, sys

htmlFile = 'webpage.txt'
prefix = 'https://downloads.khinsider.com'
songTitleList = []

print("-- KHINSIDER SCRAPER --")
print("V. 1.0")

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

    trackCount = 0
    hrefList = []
    print('[scraper] Scraping list of links from site...')
    for item in selection:
        link = item.get('href')
        songTitle = item.parent.parent.find('td', class_="clickable-row").a.string
        songTitleList.append(songTitle.replace(' ', '_'))

        hrefList.append('{}{}'.format(prefix, link))
        trackCount += 1
    print('[scraper] Found {} tracks.'.format(trackCount))

    return hrefList

def scrapeSongLinks(hrefList):
    trackCount = len(hrefList)
    count = 1
    sleepTimer = 20 if trackCount < 26 else 15
    timeOfArrival = (sleepTimer * trackCount) / 60
    print('[i] Grabbing download links in {} second intervals.'.format(sleepTimer))
    print('[i] This is estimated to take {} minutes'.format(round(timeOfArrival, 2)))
    linkData = open('./downloadedTracks/linkData.txt', 'w')
    for trackPage in hrefList:
        res = requests.get(trackPage)
        type(res)

        res.raise_for_status()

        parsedHtml = bs4.BeautifulSoup(res.text, features="html.parser")
        selection = parsedHtml.find('span', class_="songDownloadLink")

        link = selection.parent['href']
        songTitle = songTitleList.pop(0)

        linkData.write('{} -o {}.mp3\n'.format(link, songTitle))

        print('\n TRACK {} OF {}'.format(count, trackCount))
        print(' TITLE : {}'.format(songTitle))
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
    hrefs = scrapeHrefs(html)
    scrapeSongLinks(hrefs)
    
    print('\n[khscraper] Finished!')

main()
