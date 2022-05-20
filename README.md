# tool

## Introduction


## How to Install and Run the tool
### Tor Setup <img src="https://upload.wikimedia.org/wikipedia/commons/c/c9/Tor_Browser_icon.svg" height="40" width="40" align='center' title="TorBrowser">
        

1) First of all install tor browser in your computer 
2) Open the terminal and then go to the location where tor.exe file is present (It might be under main Tor folder/Browser/TorBrowser)
3) Run this command in terminal and put your password there ``` tor ---hash-password <your_password> | more ```
4) Then it will generate hash password copy that password 
5) Then Go to the location Tor_Browser\Browser\TorBrowser\Data\Tor and open torrc file
6) write this in torrc file (hashpassword is the one you copied earlier)
```
   ControlPort 9051 
   HashedControlPassword <hash_password>
```
### Tool Setup
1) Clone this repository using and open the tool in code editor
```
$ git clone https://github.com/pranav750/SpyDark](https://github.com/pranav750/tool.git
```
2) Get in the tool directory and install the dependencies:
```
$ pip install -r requirements.txt
```
3) Create a .env file in the parent directory and put variable values as guided in .env.sample file

### How to use Tool

Commands
<ul>
   <li>dark :  crawling the dark web</li>
   <li>surface : crawling the surface web</li>
   <li>url : url that is used to crawl</li>
   <li>multi : multithreaded algorithm used for crawling</li>
   <li>BFS : breadth first search used for crawling</li>
   <li>DFS : depth first search used for crawling</li>
   <li>depth : number of depth used for crawling</li>
