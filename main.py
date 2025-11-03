import requests
from bs4 import BeautifulSoup

def getForumHome():
    request = requests.get("https://scratch.mit.edu/discuss", verify=False) #because of the stupid BYOD
    req_text = request.text
    soup = BeautifulSoup(req_text, features="html.parser")
    #print(soup)
    categories = []
    # Let's get the forums first.
    idx1 = soup.select_one("#idx1") #get the container with the categories
    for category in idx1.select(".box"):
        #forum_tr.select_one("tr .tcl .intd .tclcon h3").text.split("\n")[0]
        category_name = category.select_one(".box-head h4").text.split("\nToggle shoutbox\n                ")[1].split("\n")[0]
        category_dict = {
            "category_name": category_name,
            "forums": []
        }
        forum_tbody = category.select(".box-content table tbody")
        for forum_tr in forum_tbody:
            forum_name = forum_tr.select_one("tr .tcl .intd .tclcon h3").text.split("\n")[0]
            forum_id = forum_tr.select_one("tr .tcl .intd .tclcon h3 a").get("href").split("/discuss/")[1].split("/")[0]
            forum_desc_tag = forum_tr.select_one("tr .tcl .intd .tclcon")
            print("oegoirg")
            print(forum_desc_tag)
            try:
                forum_desc = forum_desc_tag.contents[-1].text.split("\n                ")[1]
            except IndexError:
                forum_desc = ""
            print(forum_desc)
            topic_count = forum_tr.select_one("tr .tc2").text
            post_count = forum_tr.select_one("tr .tc3").text
            forum_dict = {
                "title": forum_name,
                "id": int(forum_id),
                "description": forum_desc,
                "topic_count": int(topic_count),
                "post_count": int(post_count),
            }
            category_dict["forums"].append(forum_dict)
        categories.append(category_dict)
    print(categories)


