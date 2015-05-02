from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import helpers, blockchain_func
import random
from bitcoinrpc.authproxy import AuthServiceProxy as rpcRawProxy

@csrf_exempt
def config_automatic_setup(request):
    """
        Used on setup page, setup peercoin configuration for rpc_server.
    """
    forced_updates = {
        "server": "1",
        "txindex": "1"
    }
    optional_updates = {
        "rpcuser": ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(10)),
        "rpcpassword": ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(10)),
    }
    helpers.edit_config(forced_updates, optional_updates)

    conf = helpers.get_service_status()
    return HttpResponse(json.dumps({
        "status": "success",
        "config": conf
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def check_peercoin_conf(request):
    """
        Get peercoin configuration and status of gpg / wallet / transaction index.
    """
    conf = helpers.get_service_status()
    return HttpResponse(json.dumps({
        "status": "success",
        "config": conf
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def blockchain_scan_status(request):
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())
    latest_block, blocks_left = blockchain_func.get_blockchain_scan_status(rpc_raw)

    return HttpResponse(json.dumps({
        "status":"success",
        "latest_block": latest_block,
        "blocks_left": blocks_left
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def get_addresses(request):
    """
        Get all your addresses from your wallet.
    """
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())
    addresses = rpc_raw.listunspent(0)
    return HttpResponse(json.dumps({
        "status": "success",
        "data":addresses
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def setup(request):
    html = ""
    import peerapps.settings
    with open(peerapps.settings.PEERAPPS_FRONTEND_ROOT+"/setup.html") as f:
        html = f.read()
    return HttpResponse(html, content_type="text/html")
