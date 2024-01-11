# BluePidgn
BluePidgn is an open-source Botnet Command and Control (C2) framework that utilizes only default Python3 libraries. 
It has many different functions such as:
* Persistence
* Backdoor
* DDoS attacks
* Bot handling

# Setup
Change the ```[YOUR_IP]```'s in the client.pyw file to your C2 server IP

# How to run
```python3 c2server.py```

# Usage
```
[*] Server listening on 0.0.0.0:443

Commands:

1) shell  - Spawn a shell on a selected bot
2) attack - Starts DDoS attack
3) list   - Shows the list of bots connected
4) remove - Remove client/s
5) quit   - Quit DDoS attack

  ____  _              _____ _     _
 |  _ \| |            |  __ (_)   | |
 | |_) | |_   _  ___  | |__) |  __| | __ _ _ __
 |  _ <| | | | |/ _ \ |  ___/ |/ _` |/ _` | '_ \
 | |_) | | |_| |  __/ | |   | | (_| | (_| | | | |
 |____/|_|\__,_|\___| |_|   |_|\__,_|\__, |_| |_|
                                      __/ |
                                     |___/

              Made by: https://github.com/LTWeaver
              use 'help' to get started
              use 'quit' to quit (will have to reboot server if you dont use this)


Bots Connected: 0



>>>:
```
