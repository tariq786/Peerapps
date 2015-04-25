from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from django.db.models import Q
from models import Subscription, Blog

import helpers, blockchain_func
from bitcoin.rpc import Proxy as rpcProcessedProxy
from bitcoinrpc.authproxy import JSONRPCException, AuthServiceProxy as rpcRawProxy
import external_db

@csrf_exempt
def unsubscribe(request):
    """
        Unsubscribe to the blog posts of a given address.
    """
    address = request.POST.get('address')

    Subscription.objects.filter(address=address).delete()

    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def subscribe(request):
    """
        Subscribe to the blog posts of a given address.
    """
    address = request.POST.get('address')

    new_sub = Subscription(**{
        "address": address
    })
    new_sub.save()

    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def view_latest_post(request):
    """
        Get the latest blog post from external storage for a given address.
    """
    address = request.POST.get('address')
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())

    latest_blog_post = Blog.objects.filter(address_from=address).order_by('-time')

    blog_post = helpers.download_blg(rpc_raw, latest_blog_post.key, latest_blog_post.address_from)

    return HttpResponse(json.dumps({
        "status": "success",
        "data": blog_post
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def get_blogs(request):
    """
        Get all blogs from your db
    """
    address = request.POST.get('address')

    results = {
        "sub": [],
        "mine": [],
        "browse": []
    }
    my_blogs = Blog.objects.filter(~Q(msg=""), address_from=address).order_by('-time')
    for m in my_blogs:
        results['mine'].append({
            "address_from": m.address_from,
            "block_index": m.block_index,
            "tx_id": m.tx_id,
            "msg": m.msg,
            "key": m.key,
            "time": m.time
        })

    my_sub_ids = [s.address for s in Subscription.objects.all()]

    sub_blogs = Blog.objects.filter(~Q(msg=""), address_from__in=my_sub_ids).order_by("-time")
    for m in sub_blogs:
        results['sub'].append({
            "address_from": m.address_from,
            "block_index": m.block_index,
            "tx_id": m.tx_id,
            "msg": m.msg,
            "key": m.key,
            "time": m.time
        })

    browsable_blogs = {}
    browse_blogs_db = Blog.objects.filter(~Q(address_from__in=my_sub_ids)).order_by('-time')
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

    print "results", results

    return HttpResponse(json.dumps({
        "status": "success",
        "data": results
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def scan_blogs(request):
    """
        For our own blog and the blogs we are subscribing to,
            for any new blog posts we only have meta data for,
                download the blog post.
    """
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())
    helpers.download_blgs(rpc_raw)

    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def submit_blogpost(request):
    """
        Post a non-encrypted blog post that anyone can read via PeerBlogs, cost 0.01 ppc
    """
    from_address = request.POST.get('from_address')
    message = request.POST.get('message')
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())

    if request.POST.get('wallet_passphrase', False):
        rpc_raw.walletpassphrase(request.POST.get('wallet_passphrase'), 60)
    try:
        message += "|" + helpers.sign_string(rpc_raw, message, from_address)
    except JSONRPCException, e:
        if "passphrase" in e.error['message']:
            return HttpResponse(json.dumps({
                "status": "error",
                "message":"Wallet locked.",
                "type":"wallet_locked"
            }, default=helpers.json_custom_parser), content_type='application/json')
        else:
            return HttpResponse(json.dumps({
                "status": "error",
                "message":"Error while trying to sign public key."
            }, default=helpers.json_custom_parser), content_type='application/json')

    message = helpers.format_outgoing(message)
    opreturn_key = external_db.post_data(message)

    op_return_data = "pm" #program code (peermessage), 2 chars
    op_return_data += "blg" #opcode (blogpost), 3 chars
    op_return_data += opreturn_key #key pointing to external datastore

    rpc_processed = rpcProcessedProxy()
    blockchain_func.submit_opreturn(rpc_processed, from_address, op_return_data)
    return HttpResponse(json.dumps({
        "status": "success"
    }, default=helpers.json_custom_parser), content_type='application/json')

@csrf_exempt
def peerblog(request):
    return render(request, 'peerblog.html', {})
