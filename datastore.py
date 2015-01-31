import requests
import random
import hashlib
import time

def post_data(value):
    #key must NOT contain capital letters, causes opcode error
    key = hashlib.sha1(str(time.time())+value).hexdigest()[:25]
    
    #pastebin creates it's own unique key of 8 characters, which is 18 characters in hex
    #tinyurl converts underscores to dashes
    #isgd enforces key max length of 30

    pb_key = post_data_pastebin(value)
    if pb_key:
        key = key[:-16] + pb_key

    #save to tinyurl
    post_data_tinyurl(key, value)

    #save to is.gd
    post_data_isgd(key, value)

    print "KEY", key
    
    return key

def get_data(key):

    choices = ["tinyurl", "isgd", "pastebin"]
    #random.shuffle(choices)

    for i in range(3):
        #share the load
        if choices[i] == "tinyurl":
            data = get_data_tinyurl(key)
        elif choices[i] == "isgd":
            data = get_data_isgd(key)
        elif choices[i] == "pastebin":
            data = get_data_pastebin(key[-16:].decode("hex"))
            
        if data:
            break
    return data

###############
#IS.GD
###############

def get_data_isgd(key):
    final_data = ""
    iterations = 0
    while True:
        print "Retrieving chunk..."
        key_suffix = ""
        if iterations > 0:
            #on all iterations after the first, append _# to key name
            key_suffix = "_"+str(iterations)
        current_url = ""
        headers = {
            'User-Agent': get_random_useragent()
        }
        url = 'http://is.gd/a'+key+key_suffix
        print "hitting", url
        r = requests.get(url, headers=headers, cookies={'preview': '0'})
        if "http://stackoverflow.com/?" in r.url: #what is the url after following redirects?
            print "Retrieved by following redirects"
            current_url = r.url.replace("http://stackoverflow.com/?", "")

        if not current_url:
            #Alternate retrieval method that doesn't ping stackoverflow:
            r = requests.get(url, headers=headers, cookies={'preview': '1'})
            try:
                current_url = r.text.split('http://stackoverflow.com/?')[1].split('" class="biglink')[0]
            except IndexError:
                #print "Error while checking preview", r.text
                return None
            print "Retrieved by using preview"

        if current_url[-2:] == "-m":
            #first chunk of several
            print "Retrieved chunk", current_url[:-2]
            final_data += current_url[:-2]
            iterations += 1
        else:
            print "Retrieved final piece", current_url
            return final_data + current_url

def post_data_isgd(key, value):
    max_chunk_size = 1500
    indx = 0
    iterations = 0
    value_length = len(value)
    while (indx < value_length):
        value_suffix = ""
        key_suffix = ""
        if iterations > 0:
            #on all iterations after the first, append _# to key name
            key_suffix = "_"+str(iterations)
        if (indx+max_chunk_size) < value_length:
            #if there are more chunks, append -m to the value
            value_suffix = "-m"
        headers = {
            'User-Agent': get_random_useragent()
        }
        postdata = {
            "url": "http://stackoverflow.com/?"+value[indx:indx+max_chunk_size]+value_suffix,
            "format": "json",
            "shorturl": key+key_suffix
        }
        print "CREATED", "http://is.gd/"+postdata['shorturl']
        requests.post('http://is.gd/create.php', params=postdata, headers=headers)
        indx += max_chunk_size
        iterations += 1



###############
#TINYURL
###############

def get_data_tinyurl(key):
    final_data = ""
    iterations = 0
    while True:
        key_suffix = ""
        if iterations > 0:
            #on all iterations after the first, append -# to key name
            key_suffix = "-"+str(iterations)
        current_url = ""
        headers = {
            'User-Agent': get_random_useragent()
        }
        url = 'http://tinyurl.com/1'+key+key_suffix
        print "hitting", url
        try:
            r = requests.get(url, headers=headers)
            if "http://stackoverflow.com/?" in r.url: #what is the url after following redirects?
                print "Retrieved by following redirects"
                current_url = r.url.replace("http://stackoverflow.com/?", "")
        except requests.exceptions.ConnectionError:
            pass

        if not current_url:
            #Alternate retrieval method that doesn't ping stackoverflow:
            url = 'http://preview.tinyurl.com/1'+key+key_suffix
            r = requests.get(url, headers=headers)
            try:
                current_url = r.text.split('http://stackoverflow.com/?')[1].split('</b>')[0].replace("<br />", "")
            except IndexError:
                #print "Error while checking preview", r.text
                return None
            print "Retrieved by using preview"

        if current_url[-2:] == "-m":
            #first chunk of several
            #print "Retrieved chunk", current_url[:-2]
            final_data += current_url[:-2]
            iterations += 1
        else:
            #print "Retrieved final piece", current_url
            return final_data + current_url

def post_data_tinyurl(key, value):
    max_chunk_size = 1800
    indx = 0
    iterations = 0  
    value_length = len(value)
    while (indx < value_length):
        value_suffix = ""
        key_suffix = ""
        if iterations > 0:
            #on all iterations after the first, append _# to key name
            key_suffix = "-"+str(iterations)
        if (indx+max_chunk_size) < value_length:
            #if there are more chunks, append -m to the value
            value_suffix = "-m"
        headers = {
            'User-Agent': get_random_useragent()
        }
        postdata = {
            "url": "http://stackoverflow.com/?"+value[indx:indx+max_chunk_size]+value_suffix,
            "submit": "Make+TinyURL%21",
            "alias": key+key_suffix
        }
        print "CREATED", "http://tinyurl.com/"+postdata['alias']
        requests.post('http://tinyurl.com/create.php', params=postdata, headers=headers)
        indx += max_chunk_size
        iterations += 1

###############
#PASTEBIN
###############

def get_data_pastebin(key):
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

def post_data_pastebin(value):
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

