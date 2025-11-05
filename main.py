import requests
from bs4 import BeautifulSoup
from termcolor import colored, cprint

def get_forum_home():
    print(colored("Get forum homepage", "grey"))
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
        forum_trs = category.select(".box-content table tbody tr")
        for forum_tr in forum_trs:
            forum_name = forum_tr.select_one("tr .tcl .intd .tclcon h3").text.split("\n")[0]
            forum_id = forum_tr.select_one("tr .tcl .intd .tclcon h3 a").get("href").split("/discuss/")[1].split("/")[0]
            forum_desc_tag = forum_tr.select_one("tr .tcl .intd .tclcon")
            try:
                forum_desc = forum_desc_tag.contents[-1].text.split("\n                ")[1]
            except IndexError:
                forum_desc = ""
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
    return categories

def print_forum_info(categories: list):
    print(colored("Discussion Forums Home", "white", "on_blue"))
    for category in categories:
        testing = not len(category["forums"]) == 1 and "s"
        print(f"=== {colored(category["category_name"], "white", "on_green")} === ({len(category["forums"])} forum{testing})")
        for forum in category["forums"]:
            print(f"> {colored(forum["title"], "green")} ({colored(f"{forum["topic_count"]} topics, {forum["post_count"]} posts, (ID {forum["id"]}", "blue")})")
            if len(forum["description"]) > 0:
                print(f"   {forum["description"]}")
        print("\n")
def get_forum(forum_id):
    print(colored(f"Get forum {forum_id}", "grey"))
    request = requests.get(f"https://scratch.mit.edu/discuss/{forum_id}", verify=False)
    req_text = request.text
    soup = BeautifulSoup(req_text, features="html.parser")
    topics = []
    vf_soup = soup.select_one("#vf")
    forum_name = vf_soup.select_one(".box .box-head h4 span").text
    topic_trs = soup.select("tr")
    topic_trs.pop(0)
    for tr in topic_trs:
        topic_name = tr.select_one(".tcl .tclcon h3 a").text
        topic_id = tr.select_one(".tcl .tclcon h3 a").get("href").split("/discuss/topic/")[1].split("/")[0]
        try:
            topic_replies = tr.select_one(".tc2").text
        except AttributeError:
            topic_replies = 0
        try:
            topic_views = tr.select_one(".tc3").text
        except AttributeError:
            topic_views = 0

        topic_replies = int(topic_replies)
        topic_views = int(topic_views)

        topics.append({
            "id": topic_id,
            "name": topic_name,
            "replies": topic_replies,
            "views": topic_views
        })
    return {
        "forum_name": forum_name,
        "topics": topics
    }
def print_forum(forum):
    print(f'Current forum: {colored(forum["forum_name"], "white", "on_green")}\n')
    for topic in forum["topics"]:
        print(f"> {colored(topic["name"], "green")} (ID {colored(topic["id"], "blue")})")
        cprint(f"  {topic["replies"]}+ replies, {topic["views"]}+ views", "blue")

def get_topic(topic_id):
    request = requests.get(f"https://scratch.mit.edu/discuss/topic/{topic_id}")
    req_text = request.text
    soup = BeautifulSoup(req_text, features="html.parser")
    posts = []
    linkst_li = soup.select(".linkst ul li")
    topic_name = linkst_li[2].text
    blockposts = soup.select(".blockpost")
    for bp in blockposts:
        friendly_date = bp.select_one(".box .box-head a").text
        poster_username = bp.select_one(".username").text
        contents = bp.select_one(".post_body_html")
        post_index = int(bp.select_one(".box .box-head .conr").text[1:])
        posts.append({
            "post_index": post_index,
            "friendly_date": friendly_date,
            "poster": {
                "username": poster_username
            },
            "contents": str(contents)
        })
    return {
        "name": topic_name,
        "posts": posts
    }

def print_topic(topic):
    print(f"Current topic: {colored(topic["name"], "white", "on_green")}")
    for post in topic["posts"]:
        print(f"{colored(f"{post["poster"]["username"]}", "green")} {colored(f"({post["friendly_date"]}, #{post["post_index"]}", "blue")})")
        raw_text = post["contents"]
        text = raw_text.replace("<br/>", "\n")
        text = text.replace("</br>", "\n")
        text = text.replace("<br>", "\n")
        text = text.replace('<div class="post_body_html">', "")
        text = text.replace('</div>', "")
        text = text.replace('<div style="text-align:center;">', "") #unsupported
        text = text.replace('<span class="bb-big">', "")  # unsupported
        text = text.replace('<span class="bb-small">', "")  # unsupported
        text = text.replace('<ul>', "")  # unsupported
        text = text.replace('</ul>', "")  # unsupported
        text = text.replace('<blockquote>', "")  # unsupported (for now)
        text = text.replace('</blockquote>', "\n")
        text = text.replace('<li>', "* ")  # bulleted stuff will be replaced with a dot
        text = text.replace('</li>', "")
        text = text.replace('<span class="bb-bold">', "\033[1m")
        text = text.replace('<p class="bb-quote-author">', "\033[1m") #the quote author will be bolded, just like in web
        text = text.replace('<span class="bb-italic">', "\x1B[3m")  # unsupported
        text = text.replace('</span>', "\033[0m\x1B[0m")
        text = text.replace('</p>', "")
        text = text.replace('<a href="', " ") #remove link tag (but leave a space)
        text = text.replace('">', "") #mmm love jank
        text = text.replace('</a>', "")
        text = text
        print(text)
        print("\n")

categories = get_forum_home()
print_forum_info(categories)
while True:
    forum_id = input(f"Type a forum ID: ")
    try:
        forum_id = int(forum_id)
        break
    except ValueError:
        print("Whoops, that's not a valid forum ID.")

forum = get_forum(forum_id)
print_forum(forum)
while True:
    topic_id = input(f"Type a topic ID: ")
    try:
        topic_id = int(topic_id)
        break
    except ValueError:
        print("Whoops, that's not a valid topic ID.")

topic = get_topic(topic_id)
print_topic(topic)

