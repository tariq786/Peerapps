import random
import hashlib
import time

def post_data(value):
    import isgd, tinyurl, pastebin

    #key must NOT contain capital letters, causes opcode error
    key = hashlib.sha1(str(time.time())+value).hexdigest()[:25]
    #pastebin creates it's own unique key of 8 characters, which is 18 characters in hex
    pb_key = pastebin.post_data(value)
    if pb_key:
        key = key[:-16] + pb_key

    #tinyurl converts underscores to dashes
    tinyurl.post_data(key, value)

    #isgd enforces key max length of 30
    isgd.post_data(key, value)

    return key

def get_data(key):
    import isgd, tinyurl, pastebin
    
    #share the load
    choices = ["tinyurl", "isgd", "pastebin"]
    random.shuffle(choices)
    for c in choices:
        if c == "tinyurl":
            data = tinyurl.get_data(key)
        elif c == "isgd":
            data = isgd.get_data(key)
        elif c == "pastebin":
            try:
                data = pastebin.get_data(key[-16:].decode("hex"))
            except TypeError:
                data = None #Can occur from someone making an invalid key

        if data:
            print "data", data
            break
        
    return data


###############
# Utilities
###############

def get_random_useragent():
    return random.choice([
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; Touch)',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_3; en-us; Silk/1.1.0-80) AppleWebKit/533.16 (KHTML, like Gecko) Version/5.0 Safari/533.16 Silk-Accelerated=true',
        'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10',
        'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
        'BlackBerry9700/5.0.0.862 Profile/MIDP-2.1 Configuration/CLDC-1.1 VendorID/331 UNTRUSTED/1.0 3gpp-gba', #lulz
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
        'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'
    ])

