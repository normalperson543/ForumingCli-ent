import requests
from bs4 import BeautifulSoup
from termcolor import colored, cprint
import os
import webbrowser
import sys


def get_forum_home(suppress_request_msg = False):
    if not suppress_request_msg:
        print(colored("Get forum homepage", "blue"))
    request = requests.get("https://scratch.mit.edu/discuss")
    req_text = request.text
    soup = BeautifulSoup(req_text, features="html.parser")
    # print(soup)
    categories = []
    # Let's get the forums first.
    idx1 = soup.select_one("#idx1")  # get the container with the categories
    if not idx1:
        return categories
    for category in idx1.select(".box"):
        # forum_tr.select_one("tr .tcl .intd .tclcon h3").text.split("\n")[0]
        category_name = \
        category.select_one(".box-head h4").text.split("\nToggle shoutbox\n                ")[1].split("\n")[0]
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
        print(
            f"=== {colored(category["category_name"], "white", "on_green")} === ({len(category["forums"])} forum{testing})")
        for forum in category["forums"]:
            print(
                f"> {colored(forum["title"], "green")} ({colored(f"{forum["topic_count"]} topics, {forum["post_count"]} posts, (ID {forum["id"]}", "blue")})")
            if len(forum["description"]) > 0:
                print(f"   {forum["description"]}")
        print("\n")
    if len(categories) == 0:
        cprint("Warning: We couldn't get the forum homepage.", "white", "on_red")
        print("This may be due to the forums being down. Please try again later.")


def get_forum(forum_id, page=1, suppress_request_msg = False):
    if not suppress_request_msg:
        print(colored(f"Get forum {forum_id}", "blue"))
    request = requests.get(f"https://scratch.mit.edu/discuss/{forum_id}?page={page}")
    req_text = request.text
    soup = BeautifulSoup(req_text, features="html.parser")
    topics = []
    pagination = soup.select_one(".pagination")
    last_page = 1
    if pagination:
        last_page = int(pagination.contents[-4].text)
    vf_soup = soup.select_one("#vf")
    if not vf_soup:
        return {
            "forum_name": "",
            "id": 0,
            "current_page": 0,
            "pages": 0,
            "topics": []
        }
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

        sticky = False
        if tr.select_one(".isticky"):
            sticky = True
        closed = False
        if tr.select_one(".iclosed"):
            closed = True

        author = tr.select_one(".tcl .byuser").text.split("by ")[1]
        last_poster = ""
        last_poster_friendly_time = ""

        lp_byuser = tr.select_one(".tcr .byuser")

        if lp_byuser:
            last_poster = lp_byuser.text.split("by ")[1]

        tcr_a = tr.select_one(".tcr a")
        if tcr_a:
            last_poster_friendly_time = tcr_a.text

        topics.append({
            "id": topic_id,
            "name": topic_name,
            "replies": topic_replies,
            "views": topic_views,
            "closed": closed,
            "sticky": sticky,
            "author": author,
            "last_post": {
                "username": last_poster,
                "friendly_date": last_poster_friendly_time
            }
        })
    return {
        "forum_name": forum_name,
        "id": int(forum_id),
        "current_page": int(page),
        "pages": int(last_page),
        "topics": topics
    }


def print_forum(forum):
    if forum["id"] == 0:
        cprint("Warning: This forum could not be fetched.", "white", "on_red")
        print("This could be due to a nonexistent forum or the forums are down. Please try again later.")
        return
    print(
        f'Current forum: {colored(forum["forum_name"], "white", "on_green")} {colored(f"(page {forum["current_page"]} of {forum["pages"]})", "blue")}\n')
    for topic in forum["topics"]:
        print(
            f"> (#{forum["topics"].index(topic) + 1}) {colored(topic["name"], "green")} (ID {colored(topic["id"], "blue")}) {colored("(Sticky)", "black", "on_yellow") if topic["sticky"] else ""} {colored("Open", "white", "on_green") if not topic["closed"] else colored("Closed", "white", "on_red")}")
        cprint(f"  by {colored(topic["author"], "green")} - {topic["replies"]}+ replies, {topic["views"]}+ views", "blue")
        if not topic["last_post"]["username"] == "":
            cprint(
                f"  Last post on {colored(topic["last_post"]["friendly_date"], "green") if len(topic["last_post"]["friendly_date"]) > 0 else "an unknown date"} by {colored(topic["last_post"]["username"], "green")}",
                "blue")


def get_topic(topic_id, page=1, suppress_request_msg = False):
    if not suppress_request_msg:
        print(colored(f"Get topic {topic_id}", "blue"))
    request = requests.get(f"https://scratch.mit.edu/discuss/topic/{topic_id}?page={page}")
    req_text = request.text
    soup = BeautifulSoup(req_text, features="html.parser")
    posts = []
    linkst_li = soup.select(".linkst ul li")
    if not linkst_li:
        return {
            "name": "",
            "current_page": 0,
            "id": 0,
            "pages": 0,
            "posts": [],
            "closed": False
        }
    topic_name = linkst_li[2].contents[0].strip().split("» ")[1]
    pagination = soup.select_one(".pagination")
    last_page = 1
    if pagination:
        last_page = int(pagination.contents[-4].text)
    follow_button = soup.select_one(
        ".unfollow-button")  # Due to a bug, follow button appears on logged out and open topics
    closed = True
    if follow_button:
        closed = False
    blockposts = soup.select(".blockpost")
    for bp in blockposts:
        friendly_date = bp.select_one(".box .box-head a").text
        id = int(bp.select_one(".box .box-head a").get("href").split("/discuss/post/")[1].split("/")[0])
        poster_username = bp.select_one(".username").text
        poster_status = bp.select_one(".postleft dl").contents[4].strip()
        poster_post_count = bp.select_one(".postleft dl").contents[6].strip().split(" post")[0]
        contents = bp.select_one(".post_body_html")
        last_edit_username = ""
        last_edit_friendly_date = ""
        postedit = bp.select_one(".postedit")
        if postedit:
            postedit_text = postedit.text
            last_edit_username = postedit_text.split("Last edited by ")[1].split("(")[0]
            last_edit_friendly_date = postedit_text.split("(")[1].split(")")[0]

        post_index = int(bp.select_one(".box .box-head .conr").text[1:])

        posts.append({
            "id": id,
            "post_index": post_index,
            "friendly_date": friendly_date,
            "poster": {
                "username": poster_username,
                "status": poster_status,
                "post_count_string": poster_post_count,
            },
            "last_edit": {
                "username": last_edit_username,
                "friendly_date": last_edit_friendly_date,
            },
            "contents": str(contents)
        })
    return {
        "name": topic_name,
        "current_page": int(page),
        "id": int(topic_id),
        "pages": last_page,
        "posts": posts,
        "closed": closed
    }


def preproc_text(text):
    text = text.replace("<br/>", "\n")
    text = text.replace('<pre class="blocks">', "")
    text = text.replace('</pre>', "")
    text = text.replace("</br>", "\n")
    text = text.replace("<br>", "\n")
    text = text.replace('<div class="post_body_html">', "")
    text = text.replace('</div>', "")
    text = text.replace('<div style="text-align:center;">', "")  # unsupported
    text = text.replace('<span class="bb-big">', "")  # unsupported
    text = text.replace('<span class="bb-small">', "")  # unsupported
    text = text.replace('<p class="bb-quote-author">', "")  # unsupported
    text = text.replace('<ul>', "")  # unsupported
    text = text.replace('</ul>', "")  # unsupported

    # Emoji support

    R2_SMILES_URLS = [
        "//cdn.scratch.mit.edu/scratchr2/static/__5b3e40ec58a840b41702360e9891321b__/djangobb_forum/img/smilies",
        "//cdn.scratch.mit.edu/scratchr2/static/__35b9adb704d6d778f00a893a1b104339__/djangobb_forum/img/smilies"]
    for url in R2_SMILES_URLS:
        text = text.replace(f'<img src="{url}/big_smile.png">', ":D")
        text = text.replace(f'<img src="{url}/mad.png">', ":mad:")
        text = text.replace(f'<img src="{url}/smile.png">', ":)")
        text = text.replace(f'<img src="{url}/neutral.png">', ":|")
        text = text.replace(f'<img src="{url}/sad.png">', ":(")
        text = text.replace(f'<img src="{url}/big_smile.png">', ":D")
        text = text.replace(f'<img src="{url}/yikes.png">', ":o")
        text = text.replace(f'<img src="{url}/wink.png">', ";)")
        text = text.replace(f'<img src="{url}/hmm.png">', ":/")
        text = text.replace(f'<img src="{url}/tongue.png">', ":P")
        text = text.replace(f'<img src="{url}/lol.png">', ":lol:")
        text = text.replace(f'<img src="{url}/roll.png">', ":rolleyes:")
        text = text.replace(f'<img src="{url}/cool.png">', ":cool:")

    text = text.replace('<img src="', "")  # just give the link
    text = text.replace("</img>", "")
    text = text.replace('"/>', "")  # just give the link
    text = text.replace('<blockquote>', "")  # unsupported (for now)
    text = text.replace('</blockquote>', "\n")
    text = text.replace('<li>', "* ")  # bulleted stuff will be replaced with a dot
    text = text.replace('</li>', "")
    text = text.replace('<span class="color:">', "")  # for now...
    text = text.replace('<span class="bb-bold">', "\033[1m")
    text = text.replace('<span class="bb-underline">', "\033[4m")
    text = text.replace('<span class="bb-italic">', "\x1B[3m")
    text = text.replace('<em>', "\x1B[3m")  # unsupported
    text = text.replace('</span>', "\033[0m\x1B[0m")
    text = text.replace('</em>', "\x1B[0m")
    text = text.replace('</p>', "")
    text = text.replace('<span>', "")
    text = text.replace('<a href="', "")  # remove link tag
    text = text.replace('">', " ")  # mmm love jank
    text = text.replace('</a>', "")
    return text
def print_topic(topic):
    if topic["id"] == 0:
        cprint("Warning: The topic may not exist or the forums are down.", "white", "on_red")
        print("Please try again later.")
        return
    print(
        f"Current topic: {colored(topic["name"], "white", "on_green")} (page {topic["current_page"]} of {topic["pages"]})")
    if topic["closed"]:
        cprint("Topic CLOSED\n", "red")
    else:
        cprint("Topic OPEN\n", "green")
    for post in topic["posts"]:
        print(
            f"{colored(f"{post["poster"]["username"]}", "green")} ({colored("Scratcher", "cyan") if post["poster"]["status"] == "Scratcher" else ""}{colored("New Scratcher", "red") if post["poster"]["status"] == "New Scratcher" else ""}{colored("Teacher", "orange") if post["poster"]["status"] == "Teacher" else ""}{colored("ST", "magenta") if post["poster"]["status"] == "Scratch Team" else ""}{colored("Mod", "magenta") if post["poster"]["status"] == "Forum Moderator" else ""}, {colored(post["poster"]["post_count_string"], "blue")} posts) {colored(f"({post["friendly_date"]}, #{post["post_index"]}, ID {post["id"]}", "blue")})")
        if post["last_edit"]["username"]:
            cprint(f"Edited by {colored(post["last_edit"]["username"], "green")} on {colored(post["last_edit"]["friendly_date"], "green")}", "white", "on_magenta")
        raw_text = post["contents"]
        text = preproc_text(raw_text)
        print(text)
        print("\n")
def accept_user_input():
    answer = input("? ")
    command_split = answer.split(" ")
    global current_page, previous_forum, topic, forum, categories
    if command_split[0] == "of":
        try:
            forum_id = int(command_split[1])
            forum = get_forum(forum_id)
            os.system("clear")
            current_page = "f"
            previous_forum = forum_id
            print_forum(forum)
            return
        except ValueError:
            print("Whoops, that's not a valid forum ID.")
            return
    if command_split[0] == "ot":
        try:
            topic_id = int(command_split[1])
            topic = get_topic(topic_id)
            os.system("clear")
            current_page = "t"
            print_topic(topic)
            return
        except ValueError:
            print("Whoops, that's not a valid forum ID.")
            return
    if command_split[0] == "h":
        categories = get_forum_home()
        previous_forum = 0
        current_page = "h"
        os.system("clear")
        print_forum_info(categories)
        return
    if command_split[0] == "bb":
        if current_page == "t":
            if previous_forum == 0:
                # go home
                categories = get_forum_home()
                current_page = "h"
                os.system("clear")
                print_forum_info(categories)
                return
            else:
                # go to that forum.
                forum = get_forum(previous_forum)
                os.system("clear")
                current_page = "f"
                previous_forum = previous_forum
                print_forum(forum)
                return
        if current_page == "f":
            # go home
            categories = get_forum_home()
            current_page = "h"
            os.system("clear")
            print_forum_info(categories)
            return
        print("Nothing to go back to!")
        return
    if command_split[0] == "n":
        if current_page == "t":
            if topic["current_page"] != topic["pages"]:
                topic = get_topic(topic["id"], topic["current_page"] + 1)
                current_page = "t"
                os.system("clear")
                print_topic(topic)
                return
            print("This is the last page.")
            return
        if current_page == "f":
            if forum["current_page"] != forum["pages"]:
                forum = get_forum(forum["id"], forum["current_page"] + 1)
                current_page = "f"
                os.system("clear")
                print_forum(forum)
                return
            print("This is the last page.")
            return
        print("You need to be a topic or forum to go to the next page.")
        return
    if command_split[0] == "b":
        if current_page == "t":
            if topic["current_page"] != 1:
                topic = get_topic(topic["id"], topic["current_page"] - 1)
                current_page = "t"
                os.system("clear")
                print_topic(topic)
                return
            print("This is the first page.")
            return
        if current_page == "f":
            if forum["current_page"] != 1:
                forum = get_forum(forum["id"], forum["current_page"] - 1)
                current_page = "f"
                os.system('clear')
                print_forum(forum)
                return
            print("This is the first page.")
            return
        print("You need to be a topic or forum to go back a page.")
        return
    if command_split[0] == "o":
        if current_page == "t":
            if len(command_split) > 1 and command_split[1]:
                post_index = 0
                try:
                    post_index = int(command_split[1])
                except ValueError:
                    print("That is not a valid post index.")
                    return
                if post_index < 1 or post_index > len(topic["posts"]) - 1:
                    print("That is not a valid post index.")
                    return
                cprint("Opening the post in the browser.", "blue")
                webbrowser.open(f"https://scratch.mit.edu/discuss/post/{topic["posts"][post_index - 1]["id"]}")
                return
            cprint("Opening in the browser.", "blue")
            webbrowser.open(f"https://scratch.mit.edu/discuss/topic/{topic["id"]}")
            return
        if current_page == "f":
            cprint("Opening in the browser.", "blue")
            webbrowser.open(f"https://scratch.mit.edu/discuss/{forum["id"]}")
            return
        if current_page == "h":
            cprint("Opening in the browser.", "blue")
            webbrowser.open(f"https://scratch.mit.edu/discuss")
            return
    if command_split[0] == "p":
        try:
            page = int(command_split[1])
        except ValueError:
            print("That is not a valid page.")
            return
        if current_page == "t":
            if page >= 1 and page <= topic["pages"]:
                topic = get_topic(topic["id"], page)
                current_page = "t"
                os.system("clear")
                print_topic(topic)
                return
            print("That is not a valid page.")
            return
        if current_page == "f":
            if page >= 1 and page <= forum["pages"]:
                forum = get_forum(forum["id"], page)
                current_page = "f"
                os.system('clear')
                print_forum(forum)
                return
            print("That is not a valid page.")
            return
        print("You need to be a topic or forum to jump pages.")
        return
    if command_split[0].find("#") == 0 and current_page == "f":
        try:
            index_to_get = int(command_split[0].split("#")[1])
        except ValueError:
            print("That is not a valid index.")
            return
        try:
            topic_id = forum["topics"][index_to_get - 1]["id"]
            topic = get_topic(topic_id)
            current_page = "t"
            os.system("clear")
            print_topic(topic)
            return
        except KeyError:
            print("That is not a valid index.")
            return
    try:
        id = int(command_split[0])
        if current_page == "h":
            forum = get_forum(id)
            os.system("clear")
            current_page = "f"
            previous_forum = id
            print_forum(forum)
            return
        if current_page == "f":
            topic = get_topic(id)
            os.system("clear")
            current_page = "t"
            print_topic(topic)
            return
    except ValueError:
        pass


args = sys.argv
if len(args) > 1:
    if args[1] == "gh":
        home = get_forum_home(suppress_request_msg=True)
        if len(args) >= 3 and args[2] == "raw":
            print(home)
            exit()
        print_forum_info(home)
        exit()
    if args[1] == "gt":
        if not args[2]:
            cprint("Error: You need to specify the topic ID.", "red")
            exit(1)
        try:
            id = int(args[2])
        except ValueError:
            cprint("Error: Please specify a valid topic ID.", "red")
            exit(1)
        topic = get_topic(id, suppress_request_msg=True)
        if len(args) >= 4 and args[3] == "raw":
            print(topic)
            exit()
        print_topic(topic)
        exit()
    if args[1] == "gf":
        if not args[2]:
            cprint("Error: You need to specify the forum ID.", "red")
            exit(1)
        try:
            id = int(args[2])
        except ValueError:
            cprint("Error: Please specify a valid forum ID.", "red")
            exit(1)
        forum = get_forum(id, suppress_request_msg=True)
        if len(args) >= 4 and args[3] == "raw":
            print(forum)
            exit()
        print_forum(forum)
        exit()

def main():
    global current_page, previous_forum, topic, forum, categories
    categories = get_forum_home()
    os.system("clear")
    current_page = "h"
    previous_forum = 0
    print_forum_info(categories)
    topic = {}
    forum = {}
    categories = {}
    while True:
        accept_user_input()

if __name__ == "__main__":
    main()
