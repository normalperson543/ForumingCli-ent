# AReallyRandomCLI

A TUI (and CLI) you to view Scratch forums in a command line interface. I don't really care much about Scratch nor am I associated with their forums, it was just an excuse to use BeautifulSoup.

## Installation
```
pip install areallyrandomcli_normalperson543
```
## Usage
To go into the TUI home page:
```
areallyrandomcli
```
You'll first see the forums homepage, to go to a forum, type the corresponding ID (like 1) and press enter.

Now, you'll be in a forum page. To go to the first topic, type #1 and press Enter. For the second topic, type #2, etc.

The following shortcuts are available for navigating the TUI:
```
of [forum ID] = Opens a forum
ot [topic ID] = Opens a topic
h = Goes to the homepage
bb = Goes back one parent page
n = Goes to the next forum/topic page
b = Goes back one forum/topic page
o = Opens the current page in the browser
p [number] = Jumps to a specific page in a forum/topic
#[number] = In a forum, goes to the n-th topic  
[number] = Goes to the forum/topic with that ID
```

### Using only the CLI part
Don't want to be stuck in the TUI? can open the homepage, forums and topics using only the terminal, without interacting with the TUI.

Print out the homepage:
```
areallyrandomcli gh
```

Print out a topic:
```
areallyrandomcli gt [topic ID]
```

Print out a forum:
```
areallyrandomcli gf [forum ID]
```


You can also type ``raw`` to get the raw output of any page just after it is parsed. I don't know how you would use that but it exists.

