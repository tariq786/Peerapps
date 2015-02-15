import json
import helpers, blockchain_func
from bitcoin.rpc import Proxy as rpcProcessedProxy
from bitcoinrpc.authproxy import AuthServiceProxy as rpcRawProxy
import local_db
import external_db
import time
import os

from bottle import static_file, request, Bottle
moduleApp = Bottle()

@moduleApp.route('/autocomplete_address/')
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

@moduleApp.route('/delete_message', method='POST')
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

@moduleApp.route('/get_messages', method='POST')
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

@moduleApp.route('/transmit_message', method='POST')
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
    opreturn_key = external_db.post_data(enc_message)

    op_return_data = "pm" #program code (peermessage), 2 chars
    op_return_data += "msg" #opcode (message), 3 chars
    op_return_data += opreturn_key #key pointing to external datastore

    rpc_processed = rpcProcessedProxy()
    blockchain_func.submit_opreturn(rpc_processed, from_address, op_return_data)
    return json.dumps({"status":"success"})

@moduleApp.route('/publish_pk', method='POST')
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
    opreturn_key = external_db.post_data(pub_key)

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

@moduleApp.route('/setup_gpg', method='POST')
def setup_gpg():
    """
        Create public/private gpg keys for a given peercoin address
    """
    helpers.setup_gpg(request.forms.get('address'))
    return json.dumps({"status":"success"})

@moduleApp.route('/check_setup_status', method='POST')
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

@moduleApp.route('/get_addresses', method='POST')
def get_addresses():
    """
        Get all your addresses from your wallet.
    """
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())
    addresses = rpc_raw.listunspent(0)
    return json.dumps({"status":"success", "data":addresses}, default=helpers.json_custom_parser)

@moduleApp.route('/peermessage', method='GET')
def peermessage():
    return static_file("templates/peermessage.html", root='./modules/peermessage/')
