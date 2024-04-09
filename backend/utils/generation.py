from random import randint, randrange

import requests

try:
    usernames = open("./data/usernames.txt")
except FileNotFoundError:
    usernames = None

def random_line(afile):
    """
    Returns a random line from a file.
    """
    line = next(afile)
    for num, aline in enumerate(afile, 2):
        if randrange(num):
            continue
        line = aline
    return line

def get_random_username():
    try:
        response = requests.get(f"https://users.roblox.com/v1/users/{randint(1, 100_000_000)}")
        return response.json()["name"]
    except:
        if usernames:
            return random_line(usernames)
        else:
            return "[generation failed]" #write a proper error handler later