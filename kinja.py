from bs4 import BeautifulSoup
import urllib.request
import re
import timestring
import os
import time
#import psycopg2

notitle = 1
# Leave nextOne blank to start at the beginning of a writer's history. If the script errorred and you want to pick up where you left off, add the most recent ?startswith code that was printed out to the console here.
nextOne = ""
keepGoing = True
# Change below to the URL of the person's Kinja author profile. NOT their kinja site I.E. name.kinja.com, but their profile I.E. kinja.com/name
url = ""

while keepGoing:
    print(nextOne)
    keepGoing = False
    page = urllib.request.urlopen(url + nextOne).read()
    soup = BeautifulSoup(page, "html.parser")
    pageLinks = []
    for link in soup.findAll("a", {"class": "js_link sc-1out364-0 fwjlmD"}):
        if link.find("h1"):
            l = link.get("href")
            if l not in pageLinks:
                pageLinks.append(l)
    for link in soup.findAll("a"):
        if link.get("href") and link.get("href").startswith("?startIndex=") == True and link.get("href") != nextOne:
            nextOne = link.get("href")
            keepGoing = True
    for a in pageLinks:
        try:
            articlePage = urllib.request.urlopen(a).read()
            time.sleep(1)
        except urllib.error.HTTPError as e:
            print("Error fetching article: " + a)
            print(e)
        else:
            pageSoup = BeautifulSoup(articlePage, "html.parser")
            timeObject = pageSoup.findAll("a", {"class":"js_meta-time js_link sc-1out364-0 fwjlmD"})
            timetime = timestring.Date(timeObject[0].text)
            filepath = str(timetime.year) + "/" + str(timetime.month) + "/"
            preTitle = pageSoup.title.text
            if pageSoup.p is not None:
                if preTitle == "Jezebel":
                    preTitle = pageSoup.p.text
                    if preTitle is None:
                        preTitle = "No_title_available" + str(notitle)
                        notitle += 1
            if len(preTitle) > 50:
                preTitle = preTitle[:50]
            preTitle = preTitle.replace(" ", "_")
            postTitle = "".join([c for c in preTitle if re.match(r"\w", c)])
            fullTitle = filepath + postTitle
            if not os.path.exists(os.path.dirname(fullTitle)):
                try:
                    os.makedirs(os.path.dirname(fullTitle))
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise
            if os.path.isfile(fullTitle):
                fullTitle = fullTitle + str(notitle)
                notitle += 1
            with open(fullTitle + ".txt", "w") as f:
                f.write("HEADLINE: " + pageSoup.title.text + "\n")
                f.write("Published on " + timeObject[0].text + "\n")
                f.write("Original URL : " + a + "\n\n")
                for graf in pageSoup.findAll("p"):
                    f.write(graf.text + "\n")
