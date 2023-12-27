# metaswitch-tollfree-tool
Python Toll Free Creation tool using MetaView Web API.

This tool pulls existing config data for Ring to target, and creates a subscriber line (Toll free) and call forwards the subscriber line to Ring To target.

This was created because original Call translation was handled off switch by Toll Free provider, The syntax is for a very specific switch, this should be reviewed heavily if used again.

> **_NOTE:_** This has not been tested fully

## Using the tool
From the root directory

Install Requirements

```
pip3 install -r requirements.txt
```
Create a target list file, with a list of TNs that need to be searched

Call script and provide needed variables
```
python3 toll-free-tool.py
```


Example Run
```
/metaswitch-toll-free-tool$ python3 toll-free-tool.py
MetaView Web Username:username
Password: 
MetaViewWeb Address: 1.1.1.1
MetaViewWeb port: 8087
MetaViewWeb version (example: 9.3): 9.3
Target List File:target.csv

```
