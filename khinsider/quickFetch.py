import requests, bs4, time, sys

print("Paste link to download from khinsider: ")
page = sys.stdin.readline()
page = page.rstrip()
prefix = 'https://downloads.khinsider.com'

res = requests.get(page)
type(res)

res.raise_for_status() # Raises an exception if the download is unsuccessful

# Opens a file and saves the html data inside
saveFile = open('webHtml.txt', 'wb') # Opens in binary mode
for chunk in res.iter_content(100000):
    saveFile.write(chunk)
saveFile.close()

# Parses html into the variable
htmlFile = open('webHtml.txt')
parsedHtml = bs4.BeautifulSoup(htmlFile.read(), features="html.parser")
htmlFile.close()

# Make selection
selection = parsedHtml.select('.playlistDownloadSong a')
type(selection)

print('\nFetching list of links from site...')
trackCount = 0
hrefList = []
songTitleList = []
for item in selection:
    link = item.get('href')
    songTitle = item.parent.parent.find('td', class_="clickable-row").a.string
    songTitleList.append(songTitle.replace(' ', '_'))
    
    hrefList.append('{}{}'.format(prefix, link))
    trackCount += 1
print('\n * Found {} tracks.'.format(trackCount))

count = 1
sleepTimer = 30 if trackCount < 26 else 20
timeOfArrival = (sleepTimer * trackCount) / 60
print('\nGrabbing download links in {} second intervals.'.format(sleepTimer))
print('This is estimated to take {} minutes'.format(timeOfArrival))
linkData = open('./DownloadedTracks/linkData.txt', 'w')
for trackPage in hrefList:
    res = requests.get(trackPage)
    type(res)

    res.raise_for_status()

    parsedHtml = bs4.BeautifulSoup(res.text, features="html.parser")
    selection = parsedHtml.find('span', class_="songDownloadLink")

    link = selection.parent['href']
    songTitle = songTitleList.pop(0)

    linkData.write('{} -o {}.mp3\n'.format(link, songTitle))

    print('\n * TRACK {} OF {}'.format(count, trackCount))
    print(' * TITLE : {}'.format(songTitle))
    count += 1

    print('\nSleeping for {} seconds...'.format(sleepTimer))
    time.sleep(sleepTimer)
linkData.close()
print('\nScraper executed successfully!')
