from bitcoinrpc.authproxy import JSONRPCException

import json
import time


#Static load
from peerblog.opreturn_scanner import parse as peerblog_moduleparse
from peermessage.opreturn_scanner import parse as peermessage_moduleparse

from setup.models import BlockchainScan, MemPoolScan

def get_blockchain_scan_status(rpc_raw):
    bkscan = BlockchainScan.objects.all().first() #Attempt to pick up where we left off.
    if not bkscan: #First scan!
        bkscan = BlockchainScan(last_index=160000)
        bkscan.save()
    current_index = bkscan.last_index
    blockcount = rpc_raw.getblockcount()
    on_latest_block = True if current_index >= blockcount else False
    return on_latest_block, blockcount - current_index


def scan_block(rpc_raw):
    bkscan = BlockchainScan.objects.all().first() #Attempt to pick up where we left off.
    if not bkscan: #First scan!
        bkscan = BlockchainScan(last_index=160000)
        bkscan.save()
    current_index = bkscan.last_index
    blockcount = rpc_raw.getblockcount()
    on_latest_block = True if current_index >= blockcount else False

    processed_transactions = {}
    if on_latest_block:
        #If we are on the latest block, we'll be scanning the mempool later
        mpscan = MemPoolScan.objects.all().first()
        if not mpscan:
            mpscan = MemPoolScan(txids_scanned=json.dumps({}))
            mpscan.save()

        #get tx_ids we already scanned in mempool.
        processed_transactions = json.loads(mpscan.txids_scanned)

    try:
        block_hash = rpc_raw.getblockhash(current_index) #convert block index to hash
        print "...scanning block", current_index
        bi = rpc_raw.getblock(block_hash) #get list of tx_ids in block
        for tx_id in bi['tx']:
            if tx_id not in processed_transactions: #only process transactions once
                block_time = bi['time'] if 'time' in bi else int(time.time())
                parse_transaction(rpc_raw, tx_id, current_index, block_time)

        current_index += 1
        BlockchainScan.objects.all().update(last_index=current_index)

        if on_latest_block:
            print "wiping mempool"
            #wipe mempool scan (assume mempool transactions were added to this block)
            MemPoolScan.objects.all().update(txids_scanned="{}")
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
                parse_transaction(rpc_raw, tx_id, current_index, int(time.time()))
                processed_transactions[tx_id] = 1
                count_new += 1
        print "(found", count_new, "transactions)"

        MemPoolScan.objects.all().update(txids_scanned=json.dumps(processed_transactions))

        return True, blockcount - current_index
    return False, blockcount - current_index

def parse_transaction(rpc_raw, tx_id, block_index, block_time):
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

                peerblog_moduleparse(rpc_raw, op_return_data, from_user_address, block_index, tx_id, block_time)
                peermessage_moduleparse(rpc_raw, op_return_data, from_user_address, block_index, tx_id, block_time)


def submit_opreturn(rpc_connection, address, data):
    from bitcoin.core import CTxIn, CMutableTxOut, CScript, CMutableTransaction, COIN, CENT, b2x, b2lx
    from bitcoin.core.script import OP_CHECKSIG, OP_RETURN

    txouts = []

    unspent = sorted([y for y in rpc_connection.listunspent(0) if str(y['address']) == address], key=lambda x: hash(x['amount']))

    txins = [CTxIn(unspent[-1]['outpoint'])]

    value_in = unspent[-1]['amount']

    change_pubkey = rpc_connection.validateaddress(address)['pubkey']
    change_out = CMutableTxOut(int(value_in - 2*CENT), CScript([change_pubkey, OP_CHECKSIG]))
    digest_outs = [CMutableTxOut(CENT, CScript([OP_RETURN, data]))]
    txouts = [change_out] + digest_outs
    tx = CMutableTransaction(txins, txouts)
    
    print tx.serialize().encode('hex')
    r = rpc_connection.signrawtransaction(tx)
    assert r['complete']
    tx = r['tx']


    #print b2x(tx.serialize())
    #print len(tx.serialize()), 'bytes'
    print(b2lx(rpc_connection.sendrawtransaction(tx)))
