import random
from collections import OrderedDict


# accept header -> default values
accepted = [
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'text/html, application/xhtml+xml, image/jxr, */*',
    'text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/webp, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1'
]


def getplatform(userAgent):
    if 'Windows' in userAgent:
        return 'Windows'

    if 'Android' in userAgent:
        return 'Android'

    if 'Macintosh' in userAgent:
        return 'macOS'

    if 'iPad' or 'iPhone' in userAgent:
        return 'iOS'

    if 'CrOS' in userAgent:
        return 'Chrome OS'

    if 'Linux' in userAgent:
        return 'Linux'

    return 'Unknown'


def generateHeaders():
    with open('user-agents.txt', 'r') as f:
        userAgents = f.readlines()

    userAgent = str(random.choice(userAgents)).strip()
    platform = getplatform(userAgent)
    accept = random.choice(accepted)

    if platform == ('Android' or 'iOS'):
        mobile = "?1"
    else:
        mobile = "?0"

    headers = OrderedDict([
        ("upgrade-insecure-requests", "1"),
        ("user-agent", userAgent),
        ("accept", accept),
        ("sec-ch-ua-mobile", mobile),
        ("sec-ch-ua-platform", f"\"{platform}\""),
        ("sec-fetch-site", "none"),
        ("sec-fetch-mod", ""),
        ("sec-fetch-user", "?1"),
        ("accept-encoding", "gzip, deflate, br"),
        ("accept-language", "bg-BG,bg;q=0.9,en-US;q=0.8,en;q=0.7")
    ])

    return headers
