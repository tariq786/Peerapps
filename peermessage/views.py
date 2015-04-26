from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import os

import helpers, blockchain_func
from bitcoin.rpc import Proxy as rpcProcessedProxy
from bitcoinrpc.authproxy import JSONRPCException, AuthServiceProxy as rpcRawProxy
import external_db
from models import Message, Spamlist, GPGKey
import datetime

@csrf_exempt
def autocomplete_address(request):
    """
        Used on inbox, when sending a message returns all addresses you have public keys for
    """
    q = request.GET['term']
    pub_keys = []
    for name in os.listdir("./public_keys/"):
        if "gpg_" in name and q.lower() in name.lower():
            k = name.replace("gpg_", "")
            pub_keys.append({
                "id": k,
                "value": k
            })

    return HttpResponse(json.dumps(pub_keys, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def delete_message(request):
    """
        Delete a decrypted message from your harddrive.
    """
    tx_id = request.POST['tx_id']
    Message.objects.filter(tx_id=unicode(tx_id)).delete()

    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def remove_from_spamlist(request):
    address = request.POST['address']
    Spamlist.objects.filter(address=unicode(address)).delete()

    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def mark_address_as_spam(request):
    """
        Marks an address as a spammer. This will delete all messages from this address, and ignore future messages from them.
    """
    address = request.POST['address']
    Message.objects.filter(address_from=unicode(address)).delete()

    new_spamlist_entry = Spamlist(**{
        "address": address
    })
    new_spamlist_entry.save()

    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def get_spamlist(request):
    """
        Get list of all addresses you marked as spam
    """
    spammers = Spamlist.objects.all().order_by('-time')
    results = []
    for m in spammers:
        results.append({
            "address": m.address,
            "time": m.time
        })

    return HttpResponse(json.dumps({
        "status": "success",
        "data": results
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def get_messages(request):
    """
        Get all decrypted messages from your db for a specific address.
    """
    address = request.POST['address']
    db_messages = Message.objects.filter(address_to=address).order_by("-time")
    messages = []
    for m in db_messages:
        messages.append({
            "address_from": m.address_from,
            "address_to": m.address_to,
            "block_index": m.block_index,
            "tx_id": m.tx_id,
            "msg": m.msg,
            "key": m.key,
            "time": m.time
        })

    return HttpResponse(json.dumps({
        "status": "success",
        "data": messages
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def transmit_message(request):
    """
        Send an encrypted message via PeerMessage, cost 0.01 ppc
    """
    from_address = request.POST['from_address']
    to_address = request.POST['to_address']
    message = request.POST['message']
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())
    if not os.path.isdir(os.getcwd()+"/public_keys/gpg_"+to_address):
        return HttpResponse(json.dumps({
            "status": "error",
            "message": "No public key found for that address."
        }, default=helpers.json_custom_parser), content_type='application/json')
    
    try:
        enc_message = helpers.encrypt_string(message, to_address)
    except:
        return HttpResponse(json.dumps({
            "status": "error",
            "message": "No public key found for that address."
        }, default=helpers.json_custom_parser), content_type='application/json')

    if request.POST.get('wallet_passphrase', False):
        rpc_raw.walletpassphrase(request.POST['wallet_passphrase'], 60)
    try:
        enc_message += "|" + helpers.sign_string(rpc_raw, enc_message, from_address)
    except JSONRPCException, e:
        if "passphrase" in e.error['message']:
            return HttpResponse(json.dumps({
                "status": "error",
                "message": "Wallet locked.",
                "type": "wallet_locked"
            }, default=helpers.json_custom_parser), content_type='application/json')
        else:
            return HttpResponse(json.dumps({
                "status": "error",
                "message": "Error while trying to sign public key."
            }, default=helpers.json_custom_parser), content_type='application/json')

    enc_message = helpers.format_outgoing(enc_message)
    opreturn_key = external_db.post_data(enc_message)

    op_return_data = "pm" #program code (peermessage), 2 chars
    op_return_data += "msg" #opcode (message), 3 chars
    op_return_data += opreturn_key #key pointing to external datastore

    rpc_processed = rpcProcessedProxy()
    blockchain_func.submit_opreturn(rpc_processed, from_address, op_return_data)

    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def publish_pk(request):
    """
        Publish your public key on the blockchain, cost 0.01 ppc.
    """
    address = request.POST['address']
    try:
        pub_key = helpers.get_pk(address)
    except ValueError:
        return HttpResponse(json.dumps({
            "status": "error",
            "message": "Must create GPG keys before publishing them!"
        }, default=helpers.json_custom_parser), content_type='application/json')
    
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())
    if request.POST.get('wallet_passphrase', False):
        rpc_raw.walletpassphrase(request.POST['wallet_passphrase'], 60)
    try:
        pub_key += "|" + helpers.sign_string(rpc_raw, pub_key, address)
    except JSONRPCException, e:
        if "passphrase" in e.error['message']:
            return HttpResponse(json.dumps({
                "status": "error",
                "message": "Wallet locked.",
                "type": "wallet_locked"
            }, default=helpers.json_custom_parser), content_type='application/json')
        else:
            return HttpResponse(json.dumps({
                "status": "error",
                "message": "Error while trying to sign public key."
            }, default=helpers.json_custom_parser), content_type='application/json')

    pub_key = helpers.format_outgoing(pub_key)
    opreturn_key = external_db.post_data(pub_key)

    op_return_data = "pm" #program code (peermessage), 2 chars
    op_return_data += "pka" #opcode (public key announce), 3 chars
    op_return_data += opreturn_key #key pointing to datastore

    rpc_processed = rpcProcessedProxy()
    blockchain_func.submit_opreturn(rpc_processed, address, op_return_data)

    GPGKey.objects.filter(address=address).delete()

    published_key = GPGKey(**{
        "address": address,
        "block_index": 0,
        "tx_id": "",
        "key": opreturn_key,
        "time": datetime.datetime.now(),
        "mine": True
    })
    published_key.save()

    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def setup_gpg(request):
    """
        Create public/private gpg keys for a given peercoin address
    """
    helpers.setup_gpg(request.POST['address'])

    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def check_setup_status(request):
    """
        For a given address, check whether you have generated a private key, and published your public key.
    """
    address = request.POST['address']

    public_key_pubbed = True if GPGKey.objects.filter(address=address).exists() else False

    return HttpResponse(json.dumps({
        "status": "success",
        "gpg_keys_setup": helpers.check_gpg_status(address),
        "public_key_published": public_key_pubbed
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def peermessage(request):
    html = ""
    with open("frontend/peermessage.html") as f:
        html = f.read()
    return HttpResponse(html, content_type="text/html")

@csrf_exempt
def spamlist(request):
    html = ""
    with open("frontend/spamlist.html") as f:
        html = f.read()
    return HttpResponse(html, content_type="text/html")