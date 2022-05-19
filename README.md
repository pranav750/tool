# tool

## Introduction


## How to Install and Run the tool

1) First of all install tor browser in your computer 
2) Open the terminal and then go to the location where tor.exe file is present (It might be under main Tor folder/Browser/TorBrowser)
3) Run this command in terminal and put your password there ``` tor ---hash-password <your_password> | more ```
4) Then it will generate hash password copy that password 
5) Then Go to the loaction Tor_Browser\Browser\TorBrowser\Data\Tor and open torrc file
6) write this in torrc file (hashpassword is the one you copied earlier)
```
   ControlPort 9051 
   HashedControlPassword <hash_password>
 ```
