import json
import helpers, blockchain_func
from bitcoin.rpc import Proxy as rpcProcessedProxy
from bitcoinrpc.authproxy import JSONRPCException, AuthServiceProxy as rpcRawProxy
import local_db, external_db

from bottle import static_file, request, Bottle
moduleApp = Bottle()

@moduleApp.route('/unsubscribe', method='POST')
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

@moduleApp.route('/subscribe', method='POST')
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

@moduleApp.route('/view_latest_post', method='POST')
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

@moduleApp.route('/get_blogs', method='POST')
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

@moduleApp.route('/scan_blogs', method='POST')
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

@moduleApp.route('/submit_blogpost', method='POST')
def submit_blogpost():
    """
        Post a non-encrypted blog post that anyone can read via PeerBlogs, cost 0.01 ppc
    """
    from_address = request.forms.get('from_address')
    message = request.forms.get('message')
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())

    if request.forms.get('wallet_passphrase', False):
        rpc_raw.walletpassphrase(request.forms.get('wallet_passphrase'), 60)
    try:
        message += "|" + helpers.sign_string(rpc_raw, message, from_address)
    except JSONRPCException, e:
        if "passphrase" in e.error['message']:
            return json.dumps({"status":"error", "message":"Wallet locked.", "type":"wallet_locked"})
        else:
            return json.dumps({"status":"error", "message":"Error while trying to sign public key."})

    message = helpers.format_outgoing(message)
    opreturn_key = external_db.post_data(message)

    op_return_data = "pm" #program code (peermessage), 2 chars
    op_return_data += "blg" #opcode (blogpost), 3 chars
    op_return_data += opreturn_key #key pointing to external datastore

    rpc_processed = rpcProcessedProxy()
    blockchain_func.submit_opreturn(rpc_processed, from_address, op_return_data)
    return json.dumps({"status":"success"})

@moduleApp.route('/peerblog.html', method='GET')
def peerblog():
    return static_file("peerblog.html", root='./frontend/')
