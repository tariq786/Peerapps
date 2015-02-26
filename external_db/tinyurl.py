import requests
from __init__ import get_random_useragent

###############
#TINYURL
###############

def get_data(key):
    final_data = ""
    iterations = 0
    while True:
        key_suffix = ""
        if iterations > 10:
            return None #stop 'dem infinite loops
        if iterations > 0:
            #on all iterations after the first, append -# to key name
            key_suffix = "-"+str(iterations)
        current_url = ""
        headers = {
            'User-Agent': get_random_useragent()
        }
        url = 'http://tinyurl.com/'+key+key_suffix
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
            url = 'http://preview.tinyurl.com/'+key+key_suffix
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

def post_data(key, value):
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

