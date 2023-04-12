'''
simple interface to talk to a bot via the command line by sending a post request to the server
Useful for debugging and testing with a fixed sender_id in order to track the conversation
'''
import requests
import sys
import os
from argparse import ArgumentParser
args = ArgumentParser(description="Talk to a bot via the command line")
args.add_argument("--bot", help="The bot to talk to", required=True)
args.add_argument("--url", help="The url to talk to", default="http://localhost:8080/text_converse")
args.add_argument("--sender", help="The sender id", default="test")
if __name__ == "__main__":
    arguments = args.parse_args()
    url = arguments.url + "?" + "bot=" + arguments.bot
    while True:
        text = input("Enter text: ")
        response = requests.post(url, json={"sender":arguments.sender ,"message": text})
        dc = response.json()
        print(dc["response"])
    
    
    