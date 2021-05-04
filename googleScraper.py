import requests as r
import re
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_cors import CORS
# from timeit import default_timer as timer

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
headers = {"user-agent": USER_AGENT}

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*.everstarck.com"}})
CORS(app)


@app.route('/api')
def data():
    # Get the google url from query arguments
    query = request.args.get('query')
    googleUrl = "https://www.google.com/search?q="+query

    # Get html of the request
    html = r.get(googleUrl, headers=headers).content
    # start = timer()

    # Get parent of the info that we need
    parentDiv = str(BeautifulSoup(html, "html.parser").findAll('div', attrs={'id': 'rso'}))
    g = BeautifulSoup(parentDiv, 'html.parser').findAll(lambda tag: tag.name == 'div' and tag.get('class') == ['g'])

    data = []
    for i in range(0,len(g)):
        gString = str(g[i])
        # Url, tittle and cite
        yurDiv = str(BeautifulSoup(gString, 'html.parser').findAll('div', attrs={'class':'yuRUbf'}))

        url = BeautifulSoup(yurDiv, 'html.parser').find('a')['href']
        tittle = BeautifulSoup(yurDiv, 'html.parser').find('h3').text

        # Cite
        citeOriginal = BeautifulSoup(yurDiv, 'html.parser').find('cite')
        cite = str(citeOriginal)
        citeSmall = ""
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
            cite = citeOriginal.text


        # Descripcion
        IsZvecDiv = str(BeautifulSoup(gString, 'html.parser').findAll('div', attrs={'class':'IsZvec'}))
        # Check if it has description and date
        desc= str(BeautifulSoup(IsZvecDiv, 'html.parser').find('span'))
        descDate = ""
        # Has date
        if '<span class="f">' in desc:
            description = desc.replace('<span class="aCOpRe"><span class="f">', "")
            # Description
            desc = re.sub(r'^(.*?)\<', '<', description)
            desc = desc.replace('</span></span>', '').replace('</span><span>', '')
            # Date
            descDate = re.sub(r'(?=</span>).*$', '', description)
        else:
            desc = desc.replace('<span class="aCOpRe"><span>', "").replace('<span>', '').replace('</span></span>', '')

        # One link has more links (table tag)
        table = str(BeautifulSoup(gString, 'html.parser').find('table'))
        tableInfoDiv = BeautifulSoup(gString, 'html.parser').findAll('div', attrs={'class':'usJj9c'})
        tableInfoList = []
        for j in range(0, len(tableInfoDiv)):
            urlTable = BeautifulSoup(str(tableInfoDiv[j]), 'html.parser').find('a')['href']
            tittleTable = BeautifulSoup(str(tableInfoDiv[j]), 'html.parser').find('h3').text
            descTable = BeautifulSoup(str(tableInfoDiv[j]), 'html.parser').find('div', attrs={'class':'st'}).text
            defaultTable = {
                "id": f"table{j+1}",
                "url":urlTable,
                "tittle": tittleTable,
                "desc": descTable
            }
            tableInfoList.append(defaultTable)

        # DefaultData to add to data list
        defaultData = {
            "id": i+1,
            "url": url,
            "tittle": tittle,
            "description": {
                "date": descDate,
                "desc": desc,
            },
            "cite": {
                "big": cite,
                "small": citeSmall
            },
            "table": tableInfoList
        }

        data.append(defaultData)
    return jsonify(data)
    # print(timer() - start)

if __name__ == "__main__":
    app.run(debug=True)