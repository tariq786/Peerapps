def parse(rpc_raw, op_return_data, from_user_address, block_index, tx_id, block_time):
    from models import Blog
    if op_return_data[2:5] == "blg": #Non-Encrypted Blog Post
        if not Blog.objects.filter(key=op_return_data[5:]).exists():
            print "Found blogpost"
            new_blog = Blog(**{
                "address_from": from_user_address,
                "block_index": block_index,
                "tx_id": tx_id,
                "msg": "",
                "key": op_return_data[5:],
                "time": block_time
            })
            new_blog.save()