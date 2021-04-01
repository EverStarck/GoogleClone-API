import requests as r
import re
# import json
from bs4 import BeautifulSoup
from timeit import default_timer as timer


def scraper(html):
    # [9] tiene info k se ve chila #32 info que nos interesa
    scriptGetter = BeautifulSoup(html, "html.parser").findAll(
        'script', attrs={'nonce': re.compile('[\w\W]+')})[32]

    scriptToText = str(scriptGetter)

    obj = re.split(
        r"<script nonce=\"(?:[^\"]+)\">var ytInitialData = ({.+});<\/script>", scriptToText)[1]
    # print(obj)

    jsonData = json.loads(obj)

    myData = {
        "banner": jsonData['header']['c4TabbedHeaderRenderer']['tvBanner']['thumbnails'],
        "avatar": jsonData['metadata']['channelMetadataRenderer']['avatar']['thumbnails'],
        "channelUrl": jsonData['metadata']['channelMetadataRenderer']['channelUrl'],
        "channelInfo": {
            "subs": jsonData['header']['c4TabbedHeaderRenderer']['subscriberCountText']['simpleText'],
            "title:": jsonData['metadata']['channelMetadataRenderer']['title'],
            "description": jsonData['metadata']['channelMetadataRenderer']['description'],
            "keywords": jsonData['metadata']['channelMetadataRenderer']['keywords'],
            "isFamilySafe": jsonData['metadata']['channelMetadataRenderer']['isFamilySafe'],
        }
    }

    print(myData)


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
headers = {"user-agent": USER_AGENT}

query = "python"
googleUrl = "https://www.google.com/search?q="+query

html = r.get(googleUrl, headers=headers).content


start = timer()

parentDiv = str(BeautifulSoup(html, "html.parser").findAll('div', attrs={'class': 'hlcw0c'}))
g = BeautifulSoup(parentDiv, 'html.parser').findAll('div', attrs={'class':'g'})

data = []

for i in range(0,len(g)):
    # print(g[i])
    # print("\n" * 2)
    gString = str(g[i])

    # Link Tittle y cita
    yurDiv = str(BeautifulSoup(gString, 'html.parser').findAll('div', attrs={'class':'yuRUbf'}))
    a = BeautifulSoup(yurDiv, 'html.parser').find('a')['href']
    tittle = BeautifulSoup(yurDiv, 'html.parser').find('h3').text


    cite = str(BeautifulSoup(yurDiv, 'html.parser').find('cite'))
    # Check if cite has span tag
    if '<cite class="iUh30 Zu0yb qLRx3b tjvcx">' in cite:
        cite = cite.replace('<cite class="iUh30 Zu0yb qLRx3b tjvcx">', "").replace('</cite>', "")
        # Replace all before the <
        citeSmall = re.sub(r'^(.*?)\<', '<', cite)
        citeSmall = citeSmall.replace('<span class="dyjrff qzEoUe">', "").replace("</span>", "")
        # Replace all after the <span
        cite = re.sub(r'(?=<span).*$', '', cite)
    else:
        # cite hasn't span tag
        cite = BeautifulSoup(yurDiv, 'html.parser').find('cite').text
        citeSmall = ""

    # table = BeautifulSoup(parentDiv, 'html.parser').find('table')

    # Descripcion
    IsZvecDiv = str(BeautifulSoup(gString, 'html.parser').findAll('div', attrs={'class':'IsZvec'}))
    # Comprobar si no tiene desc y si tiene fecha
    desc = str(BeautifulSoup(IsZvecDiv, 'html.parser').findAll('span')[1])
    desc = desc.replace("<span>", "").replace("</span>", "")

    # # Main
    # print(a, "a")
    # print(tittle, "tittle")
    # print(cite, "cite")
    # # print(table, "table")
    # # Desc
    # print(desc, "desc")
    # # print(len(desc), "desc")

    defaultData = {
        "url": a,
        "tittle": tittle,
        "description": {
            "date": "",
            "desc": desc,
        },
        "cite": {
            "big": cite,
            "small": citeSmall
        },
        "table": ""
    }

    data.append(defaultData)

    # print("\n")

print(data)
print(len(data))
print(timer() - start)