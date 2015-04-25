import local_db

def parse(rpc_raw, local_db_session, op_return_data, from_user_address, block_index, tx_id, block_time):
    if op_return_data[2:5] == "blg": #Non-Encrypted Blog Post
        if not local_db_session.query(local_db.Broadcast).filter(local_db.Broadcast.key==op_return_data[5:]).first():
            print "Found blogpost"
            new_broadcast = local_db.Broadcast(**{
                "address_from": from_user_address,
                "blockindex": block_index,
                "tx_id": tx_id,
                "msg": "",
                "key": op_return_data[5:],
                "time": block_time
            })
            local_db_session.add(new_broadcast)
            local_db_session.commit()