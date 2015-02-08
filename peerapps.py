import json
import datastore, helpers, blockchain_func
from bottle import route, run, static_file, request, redirect
from bitcoin.rpc import Proxy as rpcProcessedProxy
from bitcoinrpc.authproxy import AuthServiceProxy as rpcRawProxy

import local_db
import time
import webbrowser
import os
import random

local_db.setup()

@route('/set_reindex/', method='POST')
def set_reindex():
    """
        Used on setup page, toggle reindex to on/off in peercoin configuration.
    """
    forced_updates = {
        "reindex": request.forms.get('value')
    }
    helpers.edit_config(forced_updates)

    conf = helpers.get_service_status()
    return json.dumps({"status":"success", "config":conf})

@route('/config_automatic_setup/', method='POST')
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


@route('/autocomplete_address/')
def autocomplete_address():
    """
        Used on inbox, when sending a message returns all addresses you have public keys for
    """
    q = request.query.get('term')
    pub_keys = []
    for name in os.listdir("./public_keys/"):
        if "gpg_" in name and q.lower() in name.lower():
            k = name.replace("gpg_", "")
            pub_keys.append({
                "id": k,
                "value": k
            })

    return json.dumps(pub_keys)

@route('/check_peercoin_conf', method='POST')
def check_peercoin_conf():
    """
        Get peercoin configuration and status of gpg / wallet / transaction index.
    """
    conf = helpers.get_service_status()
    return json.dumps({"status":"success", "config":conf})

@route('/delete_message', method='POST')
def delete_message():
    """
        Delete a decrypted message from your harddrive.
    """
    local_db_session = local_db.get_session()
    tx_id = request.forms.get('tx_id')
    local_db_session.query(local_db.Message).filter(local_db.Message.tx_id==unicode(tx_id)).delete()
    local_db_session.commit()
    return json.dumps({
        "status": "success"
    })

@route('/get_messages', method='POST')
def get_messages():
    """
        Get all decrypted messages from your db for a specific address.
    """
    local_db_session = local_db.get_session()
    address = request.forms.get('address')
    db_messages = local_db_session.query(local_db.Message).filter(local_db.Message.address_to == address).order_by(local_db.Message.time.desc())
    messages = []
    for m in db_messages:
        messages.append({
            "address_from": m.address_from,
            "address_to": m.address_to,
            "blockindex": m.blockindex,
            "tx_id": m.tx_id,
            "msg": m.msg,
            "key": m.key,
            "time": m.time
        })
    return json.dumps({
        "status": "success",
        "data": messages
    })

@route('/scan_blockchain', method='POST')
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

@route('/unsubscribe', method='POST')
def unsubscribe():
    """
        Unsubscribe to the blog posts of a given address.
    """
    address = request.forms.get('address')
    local_db_session = local_db.get_session()

    local_db_session.query(local_db.Subscription).filter(local_db.Subscription.address == address).delete()
    local_db_session.commit()

    return json.dumps({
        "status": "success"
    })

@route('/subscribe', method='POST')
def subscribe():
    """
        Subscribe to the blog posts of a given address.
    """
    address = request.forms.get('address')
    local_db_session = local_db.get_session()

    new_sub = local_db.Subscription(**{
        "address": address
    })
    local_db_session.add(new_sub)
    local_db_session.commit()

    return json.dumps({
        "status": "success"
    })

@route('/view_latest_post', method='POST')
def view_latest_post():
    """
        Get the latest blog post from external storage for a given address. 
    """
    address = request.forms.get('address')
    local_db_session = local_db.get_session()
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())

    latest_blog_post = local_db_session.query(local_db.Broadcast).filter(local_db.Broadcast.address_from == address).order_by(local_db.Broadcast.time.desc()).first()

    blog_post = helpers.download_blg(rpc_raw, latest_blog_post.key, latest_blog_post.address_from)

    return json.dumps({
        "status": "success",
        "data": blog_post
    })

@route('/get_blogs', method='POST')
def get_blogs():
    """
        Get all blogs from your db
    """
    local_db_session = local_db.get_session()
    address = request.forms.get('address')

    results = {
        "sub": [],
        "mine": [],
        "browse": []
    }
    my_blogs = local_db_session.query(local_db.Broadcast).filter(local_db.Broadcast.msg != "").filter(local_db.Broadcast.address_from == address).order_by(local_db.Broadcast.time.desc())
    for m in my_blogs:
        results['mine'].append({
            "address_from": m.address_from,
            "blockindex": m.blockindex,
            "tx_id": m.tx_id,
            "msg": m.msg,
            "key": m.key,
            "time": m.time
        })

    my_sub_ids = [s.address for s in local_db_session.query(local_db.Subscription)]

    sub_blogs = local_db_session.query(local_db.Broadcast).filter(local_db.Broadcast.msg != "").filter(local_db.Broadcast.address_from.in_(tuple(my_sub_ids))).order_by(local_db.Broadcast.time.desc())
    for m in sub_blogs:
        results['sub'].append({
            "address_from": m.address_from,
            "blockindex": m.blockindex,
            "tx_id": m.tx_id,
            "msg": m.msg,
            "key": m.key,
            "time": m.time
        })

    browsable_blogs = {}
    browse_blogs_db = local_db_session.query(local_db.Broadcast).filter(~local_db.Broadcast.address_from.in_(my_sub_ids)).order_by(local_db.Broadcast.time.desc())
    for m in browse_blogs_db:
        if m.address_from not in browsable_blogs:
            browsable_blogs[m.address_from] = {
                "address_from": m.address_from,
                "latest_post_time": m.time,
                "total_posts": 1
            }
        else:
            browsable_blogs[m.address_from]['total_posts'] += 1

    results['browse'] = sorted(browsable_blogs.values(), key=lambda k: k['latest_post_time'])

    return json.dumps({
        "status": "success",
        "data": results
    })

@route('/scan_blogs', method='POST')
def scan_blogs():
    """
        For our own blog and the blogs we are subscribing to,
            for any new blog posts we only have meta data for,
                download the blog post.
    """
    local_db_session = local_db.get_session()
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())
    helpers.download_blgs(rpc_raw, local_db_session)

    return json.dumps({
        "status":"success"
    })

@route('/submit_blogpost', method='POST')
def submit_blogpost():
    """
        Post a non-encrypted blog post that anyone can read via PeerBlogs, cost 0.01 ppc
    """
    from_address = request.forms.get('from_address')
    message = request.forms.get('message')
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())

    message += "|" + helpers.sign_string(rpc_raw, message, from_address)
    message = helpers.format_outgoing(message)
    opreturn_key = datastore.post_data(message)

    op_return_data = "pm" #program code (peermessage), 2 chars
    op_return_data += "blg" #opcode (blogpost), 3 chars
    op_return_data += opreturn_key #key pointing to datastore

    rpc_processed = rpcProcessedProxy()
    blockchain_func.submit_opreturn(rpc_processed, from_address, op_return_data)
    return json.dumps({"status":"success"})

@route('/transmit_message', method='POST')
def transmit_message():
    """
        Send an encrypted message via PeerMessage, cost 0.01 ppc
    """
    from_address = request.forms.get('from_address')
    to_address = request.forms.get('to_address')
    message = request.forms.get('message')
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())
    if not os.path.isdir(os.getcwd()+"/public_keys/gpg_"+to_address):
        return json.dumps({"status":"error", "msg":"No public key found for that address."})
    try:
        enc_message = helpers.encrypt_string(message, to_address)
    except IOError:
        return json.dumps({"status":"error", "msg":"No public key found for that address."})

    enc_message += "|" + helpers.sign_string(rpc_raw, enc_message, from_address)
    enc_message = helpers.format_outgoing(enc_message)
    opreturn_key = datastore.post_data(enc_message)

    op_return_data = "pm" #program code (peermessage), 2 chars
    op_return_data += "msg" #opcode (message), 3 chars
    op_return_data += opreturn_key #key pointing to datastore

    rpc_processed = rpcProcessedProxy()
    blockchain_func.submit_opreturn(rpc_processed, from_address, op_return_data)
    return json.dumps({"status":"success"})

@route('/publish_pk', method='POST')
def publish_pk():
    """
        Publish your public key on the blockchain, cost 0.01 ppc.
    """
    address = request.forms.get('address')
    try:
        pub_key = helpers.get_pk(address)
    except ValueError:
        return json.dumps({"status":"error", "message":"Must create GPG keys before publishing them!"})
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())
    pub_key += "|" + helpers.sign_string(rpc_raw, pub_key, address)
    pub_key = helpers.format_outgoing(pub_key)
    opreturn_key = datastore.post_data(pub_key)

    op_return_data = "pm" #program code (peermessage), 2 chars
    op_return_data += "pka" #opcode (public key announce), 3 chars
    op_return_data += opreturn_key #key pointing to datastore

    rpc_processed = rpcProcessedProxy()
    blockchain_func.submit_opreturn(rpc_processed, address, op_return_data)

    local_db_session = local_db.get_session()
    local_db_session.query(local_db.MyKey).filter(local_db.MyKey.address==address).delete()
    local_db_session.commit()

    published_key = local_db.MyKey(**{
        "address": address,
        "blockindex": 0,
        "tx_id": "",
        "key": opreturn_key,
        "time": int(time.time())
    })
    local_db_session.add(published_key)
    local_db_session.commit()

    return json.dumps({"status":"success"})

@route('/setup_gpg', method='POST')
def setup_gpg():
    """
        Create public/private gpg keys for a given peercoin address
    """
    helpers.setup_gpg(request.forms.get('address'))
    return json.dumps({"status":"success"})

@route('/check_setup_status', method='POST')
def check_setup_status():
    """
        For a given address, check whether you have generated a private key, and published your public key.
    """
    address = request.forms.get('address')
    local_db_session = local_db.get_session()
    public_key_pubbed = True if local_db_session.query(local_db.MyKey).filter(local_db.MyKey.address==address).first() else False
    return json.dumps({
        "status": "success",
        "gpg_keys_setup": helpers.check_gpg_status(address),
        "public_key_published": public_key_pubbed
    })

@route('/get_addresses', method='POST')
def get_addresses():
    """
        Get all your addresses from your wallet.
    """
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())
    addresses = rpc_raw.listunspent(0)
    return json.dumps({"status":"success", "data":addresses}, default=helpers.json_custom_parser)

@route('/')
def base():
    try:
        rpc_raw = rpcRawProxy(helpers.get_rpc_url())
        rpc_raw.getblockcount()
        redirect("/peermessage")
    except IOError:
        redirect("/setup")

@route('/peerblog')
def peerblog():
    return static_file("templates/peerblog.html", root='./')

@route('/peermessage')
def peermessage():
    return static_file("templates/peermessage.html", root='./')

@route('/setup')
def setup():
    return static_file("templates/setup.html", root='./')

@route('/static/:filename#.*#')
def send_static(filename):
    return static_file(filename, root='./static/')

webbrowser.open("http://127.0.0.1:8011/setup")
run(host='127.0.0.1', port=8011, server='cherrypy')