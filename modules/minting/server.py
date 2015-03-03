import json
import helpers

import time
from bitcoinrpc.authproxy import JSONRPCException, AuthServiceProxy as rpcRawProxy
from bottle import static_file, Bottle
moduleApp = Bottle()

@moduleApp.route('/peercoin_minting_data', method='GET')
def peercoin_minting_data():
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())
    difficulty = rpc_raw.getdifficulty()
    minting_data = []
    for a in rpc_raw.listunspent(0):
        tx_info = rpc_raw.decoderawtransaction(rpc_raw.getrawtransaction(a['txid']))
        age = int(time.time()) - tx_info['time']
        age = int(((age / 60) / 60) / 24) #convert to days
        if age < 30:
            coindays = 0
        elif age < 120:
            coindays = int((age-30) * a['amount'])
        else:
            coindays = int(90 * a['amount'])
        minting_data.append([
            a['txid'],
            a['address'],
            age,
            str(a['amount']),
            coindays,
            ""
        ])

    return json.dumps({"status":"success", "difficulty": str(difficulty['proof-of-stake']), "data": minting_data})

@moduleApp.route('/peercoin_minting.html', method='GET')
def peercoin_minting():
    return static_file("peercoin_minting.html", root='./frontend/')
