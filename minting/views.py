from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import helpers
from bitcoinrpc.authproxy import AuthServiceProxy as rpcRawProxy
import time

@csrf_exempt
def peercoin_minting_data(request):
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

    return HttpResponse(json.dumps({
        "status": "success",
        "difficulty": str(difficulty['proof-of-stake']),
        "data": minting_data
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def peercoin_minting(request):
    html = ""
    import peerapps.settings
    with open(peerapps.settings.PEERAPPS_FRONTEND_ROOT+"/peercoin_minting.html") as f:
        html = f.read()
    return HttpResponse(html, content_type="text/html")
