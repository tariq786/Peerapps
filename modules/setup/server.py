import json
import helpers
import random

from bottle import static_file, Bottle
moduleApp = Bottle()

@moduleApp.route('/config_automatic_setup', method='POST')
def config_automatic_setup():
    """
        Used on setup page, setup peercoin configuration for rpc_server.
    """
    forced_updates = {
        "server": "1",
        "txindex": "1"
    }
    optional_updates = {
        "rpcuser": ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ' + '0123456789') for _ in range(10)),
        "rpcpassword": ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ' + '0123456789') for _ in range(10)),
    }
    helpers.edit_config(forced_updates, optional_updates)

    conf = helpers.get_service_status()
    return json.dumps({"status":"success", "config":conf})

@moduleApp.route('/check_peercoin_conf', method='POST')
def check_peercoin_conf():
    """
        Get peercoin configuration and status of gpg / wallet / transaction index.
    """
    conf = helpers.get_service_status()
    return json.dumps({"status":"success", "config":conf})

@moduleApp.route('/setup', method='GET')
def setup():
    return static_file("setup.html", root='./static/templates/')
