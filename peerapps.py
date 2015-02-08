import json
import helpers, blockchain_func
from bitcoinrpc.authproxy import AuthServiceProxy as rpcRawProxy
import local_db
import webbrowser
import os

#clear out pyc files
#find . -name '*.pyc' -delete

from bottle import static_file, redirect, Bottle, request
rootApp = Bottle()

import sys
sys.path.append('./')

local_db.setup()

@rootApp.route('/scan_blockchain', method='POST')
def scan_blockchain():
    """
        Scan one block in the blockchain (and optionally mempool as well)
    """
    local_db_session = local_db.get_session()
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())
    latest_block, blocks_left = blockchain_func.scan_block(rpc_raw, local_db_session)
    return json.dumps({
        "status":"success",
        "latest_block": latest_block,
        "blocks_left": blocks_left
    })

@rootApp.route('/')
def base():
    redirect("/setup")

@rootApp.route('/static/:filename#.*#')
def send_static(filename):
    import pdb; pdb.set_trace()
    return static_file(filename, root='./static/')

for name in os.listdir("./modules/"):
    if os.path.isfile("./modules/"+name+"/server.py"):
        exec "from modules."+name+".server import moduleApp as "+name+"_moduleApp"
        rootApp.merge(globals()[name+"_moduleApp"])

webbrowser.open("http://127.0.0.1:8011/setup")
rootApp.run(host='127.0.0.1', port=8011, server='cherrypy')