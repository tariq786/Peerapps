import os
import datastore
import local_db
from bitcoinrpc.authproxy import JSONRPCException

from sqlalchemy.sql import update
import json
import time
import helpers

import shutil

def scan_block(rpc_raw, local_db_session):
    bkscan = local_db_session.query(local_db.BlockchainScan).first() #Attempt to pick up where we left off.
    if not bkscan: #First scan!
        bkscan = local_db.BlockchainScan(last_index=341355)
        local_db_session.add(bkscan)
        local_db_session.commit()
    current_index = bkscan.last_index
    blockcount = rpc_raw.getblockcount()
    on_latest_block = True if current_index >= blockcount else False

    processed_transactions = {}
    if on_latest_block:
        #If we are on the latest block, we'll be scanning the mempool later
        mpscan = local_db_session.query(local_db.MemPoolScan).first()
        if not mpscan:
            mpscan = local_db.MemPoolScan(txids_scanned=json.dumps({}))
            local_db_session.add(mpscan)
            local_db_session.commit()
            
        #get tx_ids we already scanned in mempool.
        processed_transactions = json.loads(mpscan.txids_scanned)

    try:
        block_hash = rpc_raw.getblockhash(current_index) #convert block index to hash
        print "...scanning block", current_index
        bi = rpc_raw.getblock(block_hash) #get list of tx_ids in block
        for tx_id in bi['tx']:
            if tx_id not in processed_transactions: #only process transactions once
                block_time = bi['time'] if 'time' in bi else int(time.time())
                parse_transaction(rpc_raw, local_db_session, tx_id, current_index, block_time)

        current_index += 1
        u = update(local_db.BlockchainScan).values({"last_index": current_index})
        local_db_session.execute(u)
        local_db_session.commit()

        if on_latest_block:
            print "wiping mempool"
            #wipe mempool scan (assume mempool transactions were added to this block)
            u = update(local_db.MemPoolScan).values({"txids_scanned": "{}"})
            local_db_session.execute(u)
            local_db_session.commit()
            processed_transactions = {}
        
    except JSONRPCException:
        pass #at last block

    if on_latest_block:
        #Let's scan that mempool!
        print "processing mempool..."
        unconfirmed_transactions = rpc_raw.getrawmempool()
        count_new = 0
        for tx_id in unconfirmed_transactions:
            if tx_id not in processed_transactions:
                parse_transaction(rpc_raw, local_db_session, tx_id, current_index, int(time.time()))
                processed_transactions[tx_id] = 1
                count_new += 1
        print "(found", count_new, "transactions)"

        u = update(local_db.MemPoolScan).values({"txids_scanned": json.dumps(processed_transactions)})
        local_db_session.execute(u)
        local_db_session.commit()

        return True, blockcount - current_index
    return False, blockcount - current_index

def parse_transaction(rpc_raw, local_db_session, tx_id, block_index, block_time):
    tx_info = rpc_raw.decoderawtransaction(rpc_raw.getrawtransaction(tx_id))
    for vout in tx_info['vout']:
        if vout['scriptPubKey']['asm'].startswith("OP_RETURN"):
            try:
                op_return_data = vout['scriptPubKey']['asm'].split(' ')[1].decode('hex')
            except:
                continue

            if op_return_data[:2] == "pm": #PeerMessage transaction
                print "***********op_return_data", op_return_data
                addresses = []
                for inp in tx_info['vin']:
                    input_raw_tx = rpc_raw.decoderawtransaction(rpc_raw.getrawtransaction(inp['txid']))
                    addresses.append(input_raw_tx['vout'][inp['vout']]['scriptPubKey']['addresses'][0])
                from_user_address = addresses[0]

                parse_pka(rpc_raw, local_db_session, op_return_data, from_user_address, block_index, tx_id, block_time)
                parse_msg(rpc_raw, local_db_session, op_return_data, from_user_address, block_index, tx_id, block_time)
                parse_blg(rpc_raw, local_db_session, op_return_data, from_user_address, block_index, tx_id, block_time)

def parse_pka(rpc_raw, local_db_session, op_return_data, from_user_address, block_index, tx_id, block_time):
    found_data = datastore.get_data(op_return_data[5:])
    if op_return_data[2:5] == "pka": #Public Key Announcement
        if not local_db_session.query(local_db.PublicKey).filter(local_db.PublicKey.key==op_return_data[5:]).first():
            format_public_key = helpers.format_incoming(found_data)
            try:
                verified_public_key = helpers.verify_and_strip_signature(rpc_raw, format_public_key, from_user_address)
            except AssertionError:
                print "Signature invalid, skip public key."
                return

            #delete existing from disk and database
            shutil.rmtree('/public_keys/gpg_'+from_user_address, ignore_errors=True)
            local_db_session.query(local_db.PublicKey).filter(local_db.PublicKey.address==from_user_address).delete()
            local_db_session.commit()

            helpers.save_public_key(from_user_address, verified_public_key)

            new_pub_key = local_db.PublicKey(**{
                "address": from_user_address,
                "blockindex": block_index,
                "tx_id": tx_id,
                "key": op_return_data[5:],
                "time": block_time
            })
            local_db_session.add(new_pub_key)
            local_db_session.commit()

def parse_msg(rpc_raw, local_db_session, op_return_data, from_user_address, block_index, tx_id, block_time):
    found_data = datastore.get_data(op_return_data[5:])
    if op_return_data[2:5] == "msg": #Encrypted Message
        if not local_db_session.query(local_db.Message).filter(local_db.Message.key==op_return_data[5:]).first():
            if not found_data:
                print "Unable to retrieve message, skipping"
                return
            formatted_message = helpers.format_incoming(found_data)
            try:
                verified_message = helpers.verify_and_strip_signature(rpc_raw, formatted_message, from_user_address)
            except AssertionError:
                print "Signature invalid, skip message."
                return
            except AttributeError:
                print "Unable to pull message from external data source."
                return
            my_addresses = []
            for name in os.listdir("./my_keys/"):
                if "gpg_" in name:
                    my_addresses.append(name.replace("gpg_", ""))
            for to_user_address in my_addresses:
                dec_message = helpers.decrypt_string(verified_message, to_user_address)
                if dec_message:
                    new_msg = local_db.Message(**{
                        "address_from": from_user_address,
                        "address_to": to_user_address,
                        "blockindex": block_index,
                        "tx_id": tx_id,
                        "msg": dec_message.decode('utf8'),
                        "key": op_return_data[5:],
                        "time": block_time
                    })
                    local_db_session.add(new_msg)
                    local_db_session.commit()
                    break

def parse_blg(rpc_raw, local_db_session, op_return_data, from_user_address, block_index, tx_id, block_time):
    if op_return_data[2:5] == "blg": #Non-Encrypted Blog Post
        if not local_db_session.query(local_db.Broadcast).filter(local_db.Broadcast.key==op_return_data[5:]).first():
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

def submit_opreturn(rpc_connection, address, data):
    from bitcoin.core import CTxIn, CMutableTxOut, MAX_MONEY, CScript, CMutableTransaction, COIN, b2x, b2lx
    from bitcoin.core.script import OP_CHECKSIG, OP_RETURN

    txouts = []

    unspent = sorted([y for y in rpc_connection.listunspent(0) if str(y['address']) == address], key=lambda x: hash(x['amount']))

    txins = [CTxIn(unspent[-1]['outpoint'])]

    value_in = unspent[-1]['amount']

    change_pubkey = rpc_connection.validateaddress(address)['pubkey']
    change_out = CMutableTxOut(MAX_MONEY, CScript([change_pubkey, OP_CHECKSIG]))

    digest_outs = [CMutableTxOut(0, CScript([OP_RETURN, data]))]

    txouts = [change_out] + digest_outs

    tx = CMutableTransaction(txins, txouts)

    FEE_PER_BYTE = 0.00025*COIN/1000
    while True:
        tx.vout[0].nValue = int(value_in - max(len(tx.serialize()) * FEE_PER_BYTE, 0.00011*COIN))

        r = rpc_connection.signrawtransaction(tx)
        assert r['complete']
        tx = r['tx']

        if value_in - tx.vout[0].nValue >= len(tx.serialize()) * FEE_PER_BYTE:
            print b2x(tx.serialize())
            print len(tx.serialize()), 'bytes'
            print(b2lx(rpc_connection.sendrawtransaction(tx)))
            break
