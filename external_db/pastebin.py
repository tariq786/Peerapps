import requests
from __init__ import get_random_useragent

###############
#PASTEBIN
###############

def get_data(key):
    headers = {
        'User-Agent': get_random_useragent()
    }
    url = "http://pastebin.com/raw.php?i="+key
    print "hitting ", url
    r = requests.get(url, headers=headers)
    if "Pastebin.com Unknown Paste ID" in r.text:
        print "Unable to pull from pastebin."
        return None
    print "Pulled from pastebin"
    return r.text

def post_data(value):
    headers = {
        'User-Agent': get_random_useragent()
    }
    with requests.session() as c:
        t = c.get('http://pastebin.com/', headers=headers)
        post_key = t.text.split('name="post_key"')[1].split("hidden")[0].split('value="')[1].split('"')[0]
        r = c.post('http://pastebin.com/post.php', data={
            'paste_name': "",
            'paste_private': 1,
            'paste_expire_date': "N",
            "paste_format": 1,
            "paste_code": value,
            "submit_hidden": "submit_hidden",
            "post_key": post_key
        }, headers=headers)
        try:
            key = r.text.split("/raw.php?i=")[1].split('"')[0].lower()
            print "CREATED http://pastebin.com/raw.php?i=" + key
            return key.encode("hex")
        except:
            #Woah, you have reached your paste limit of 10 pastes per 24 hours. [IP-based].
            return None