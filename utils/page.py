import requests

import bs4

from utils import messages

def download_save(link, output_path):
    """ 
    Download and save a webpage as html.
    """
    messages.status("Downloading webpage...", status="page:webpage", prefix="\n")
    response = requests.get(link)
    response.raise_for_status()

    with open(output_path, 'wb') as saveFile:
        for chunk in response.iter_content(100000):
            saveFile.write(chunk)

def download(link):
    """
    Download an url
    """
    response = requests.get(link)
    response.raise_for_status()

    return response

def parse(input):
    """ 
    Read a saved html file and return a parsed object.
    """
    with open(input) as rawHtml:
        parsedHtml = bs4.BeautifulSoup(rawHtml.read(), features="html.parser")

    return parsedHtml