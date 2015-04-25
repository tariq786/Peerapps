from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import helpers
import random

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
    }), content_type='application/json')

@csrf_exempt
def check_peercoin_conf(request):
    """
        Get peercoin configuration and status of gpg / wallet / transaction index.
    """
    conf = helpers.get_service_status()
    return HttpResponse(json.dumps({
        "status": "success",
        "config": conf
    }), content_type='application/json')

@csrf_exempt
def setup(request):
    return render(request, 'setup.html', {})
