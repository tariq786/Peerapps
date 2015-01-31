import os
import gnupg #also install https://gpgtools.org/gpgsuite.html
import urllib
import datetime
from decimal import Decimal
import platform
import datastore
import local_db
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from sqlalchemy.sql import update
import json
import time

import shutil

def get_service_status():
    """
        Retrieve user configuration, and status of wallet's rpc server, transaction index, and gpg's installation.
    """
    conf = get_config()
    if 'rpcpassword' in conf and conf['rpcpassword']:
        conf['rpcpassword'] = "*******"
    try:
        rpc_raw = AuthServiceProxy(get_rpc_url())
        rpc_raw.decoderawtransaction(rpc_raw.getrawtransaction("576e6802bc6787183a329c3ebc8c7189957ab993b9cffbacb8b121f34c40c1d0"))
        conf['index_status'] = "good"
    except:
        conf['index_status'] = "bad"

    try:
        rpc_raw = AuthServiceProxy(get_rpc_url())
        rpc_raw.getblockcount()
        conf['wallet_connected_status'] = "good"
    except:
        conf['wallet_connected_status'] = "bad"

    try:
        gnupg.GPG(gnupghome=os.getcwd()+"/test_gpg_setup")
        shutil.rmtree(os.getcwd()+"/test_gpg_setup", ignore_errors=True)
        conf['gpg_suite_installed'] = "good"
    except:
        conf['gpg_suite_installed'] = "bad"

    return conf


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
                found_data = datastore.get_data(op_return_data[5:])

                if op_return_data[2:5] == "pka": #Public Key Announcement
                    if not local_db_session.query(local_db.PublicKey).filter(local_db.PublicKey.key==op_return_data[5:]).first():
                        format_public_key = format_incoming(found_data)
                        try:
                            verified_public_key = verify_and_strip_signature(rpc_raw, format_public_key, from_user_address)
                        except AssertionError:
                            print "Signature invalid, skip public key."
                            continue

                        #delete existing from disk and database
                        shutil.rmtree('/public_keys/gpg_'+from_user_address, ignore_errors=True)
                        local_db_session.query(local_db.PublicKey).filter(local_db.PublicKey.address==from_user_address).delete()
                        local_db_session.commit()

                        save_public_key(from_user_address, verified_public_key)

                        new_pub_key = local_db.PublicKey(**{
                            "address": from_user_address,
                            "blockindex": block_index,
                            "tx_id": tx_id,
                            "key": op_return_data[5:],
                            "time": block_time
                        })
                        local_db_session.add(new_pub_key)
                        local_db_session.commit()

                if op_return_data[2:5] == "msg": #Encrypted Message
                    if not local_db_session.query(local_db.Message).filter(local_db.Message.key==op_return_data[5:]).first():
                        if not found_data:
                            print "Unable to retrieve message, skipping"
                            continue
                        formatted_message = format_incoming(found_data)
                        try:
                            verified_message = verify_and_strip_signature(rpc_raw, formatted_message, from_user_address)
                        except AssertionError:
                            print "Signature invalid, skip message."
                            continue
                        except AttributeError:
                            print "Unable to pull message from external data source."
                            continue
                        my_addresses = []
                        for name in os.listdir("./my_keys/"):
                            if "gpg_" in name:
                                my_addresses.append(name.replace("gpg_", ""))
                        for to_user_address in my_addresses:
                            dec_message = decrypt_string(verified_message, to_user_address)
                            if dec_message:
                                new_pub_key = local_db.Message(**{
                                    "address_from": from_user_address,
                                    "address_to": to_user_address,
                                    "blockindex": block_index,
                                    "tx_id": tx_id,
                                    "msg": dec_message.decode('utf8'),
                                    "key": op_return_data[5:],
                                    "time": block_time
                                })
                                local_db_session.add(new_pub_key)
                                local_db_session.commit()
                                break

def edit_config(forced_updates, optional_updates=None):
    if platform.system() == 'Darwin':
        btc_conf_file = os.path.expanduser('~/Library/Application Support/Bitcoin/')
    elif platform.system() == 'Windows':
        btc_conf_file = os.path.join(os.environ['APPDATA'], 'Bitcoin')
    else:
        btc_conf_file = os.path.expanduser('~/.bitcoin')
    btc_conf_file = os.path.join(btc_conf_file, 'bitcoin.conf')

    new_file_contents = ""

    # Extract contents of bitcoin.conf to build service_url
    with open(btc_conf_file, 'r') as fd:
        # Bitcoin Core accepts empty rpcuser, not specified in btc_conf_file
        for line in fd.readlines():
            orig_line = line
            if '=' not in line:
                new_file_contents += orig_line
                continue
            if '#' in line:
                line = line[:line.index('#')]
            k, v = line.split('=', 1)
            if k in forced_updates:
                new_file_contents += k + "=" + forced_updates[k] + "\n"
                del forced_updates[k]
            elif optional_updates and k in optional_updates:
                new_file_contents += orig_line.strip() + "\n"
                del optional_updates[k]
            else:
                new_file_contents += orig_line
        for k,v in forced_updates.items():
            new_file_contents += k + "=" + v + "\n"
        if optional_updates:
            for k,v in optional_updates.items():
                new_file_contents += k + "=" + v + "\n"

    with open(btc_conf_file, 'w') as fd:
        fd.write(new_file_contents)

def get_config():
    if platform.system() == 'Darwin':
        btc_conf_file = os.path.expanduser('~/Library/Application Support/Bitcoin/')
    elif platform.system() == 'Windows':
        btc_conf_file = os.path.join(os.environ['APPDATA'], 'Bitcoin')
    else:
        btc_conf_file = os.path.expanduser('~/.bitcoin')
    btc_conf_file = os.path.join(btc_conf_file, 'bitcoin.conf')

    # Extract contents of bitcoin.conf to build service_url
    with open(btc_conf_file, 'r') as fd:
        # Bitcoin Core accepts empty rpcuser, not specified in btc_conf_file
        conf = {'rpcuser': ""}
        for line in fd.readlines():
            if '#' in line:
                line = line[:line.index('#')]
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            conf[k.strip()] = v.strip()

        service_port = 8332
        conf['rpcport'] = int(conf.get('rpcport', service_port))
        conf['rpcssl'] = conf.get('rpcssl', '0')

        if conf['rpcssl'].lower() in ('0', 'false'):
            conf['rpcssl'] = False
        elif conf['rpcssl'].lower() in ('1', 'true'):
            conf['rpcssl'] = True
        else:
            raise ValueError('Unknown rpcssl value %r' % conf['rpcssl'])

    conf['file_loc'] = btc_conf_file
    return conf

def get_rpc_url():
    conf = get_config()
    if 'rpcpassword' not in conf:
        raise ValueError('The value of rpcpassword not specified in the configuration file.')
    service_url = ('%s://%s:%s@localhost:%d' %
        ('https' if conf['rpcssl'] else 'http',
         conf['rpcuser'], conf['rpcpassword'],
         conf['rpcport']))
    return service_url


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

def get_pk(address):
    if not os.path.isdir(os.getcwd()+"/my_keys/gpg_"+address):
        raise ValueError
    gpg = gnupg.GPG(gnupghome=os.getcwd()+"/my_keys/gpg_"+address)
    return gpg.export_keys(gpg.list_keys()[0]['keyid'])

def check_gpg_status(address):
    return os.path.isdir(os.getcwd()+"/my_keys/gpg_"+address)

def save_public_key(address, key):
    pk_dir = os.getcwd()+"/public_keys/gpg_"+address+'/'
    shutil.rmtree(pk_dir, ignore_errors=True)
    os.makedirs(pk_dir)
    with open(pk_dir+'keys.asc', 'w') as f:
        f.write(key)

def setup_gpg(address):
    gpg = gnupg.GPG(gnupghome=os.getcwd()+"/my_keys/gpg_"+address)
    input_data = gpg.gen_key_input(name_email=address+'@peercoin.net')
    key = gpg.gen_key(input_data)
    ascii_armored_public_keys = gpg.export_keys(str(key))
    ascii_armored_private_keys = gpg.export_keys(str(key), True)
    with open(os.getcwd()+"/my_keys/gpg_"+address+'/keys.asc', 'w') as f:
        f.write(ascii_armored_public_keys)
        f.write(ascii_armored_private_keys)

def format_outgoing(plaintext):
    return urllib.quote_plus(plaintext.encode("base64"))

def format_incoming(plaintext):
    try:
        return urllib.unquote_plus(plaintext).decode("base64")
    except:
        return None

def sign_string(rpc_connection, plaintext, address):
    return rpc_connection.signmessage(address, plaintext)

def verify_and_strip_signature(rpc_connection, plaintext, address):
    base = plaintext.split("|")
    signature = base.pop()
    message = "|".join(base)
    assert rpc_connection.verifymessage(address, signature, message) == True
    return message

def encrypt_string(plaintext, address):
    gpg = gnupg.GPG(gnupghome=os.getcwd()+"/public_keys/gpg_"+address)
    key_data = open(os.getcwd()+"/public_keys/gpg_"+address+'/keys.asc').read()
    gpg.import_keys(key_data)
    encrypted_data = gpg.encrypt(plaintext, address+'@peercoin.net', always_trust=True)
    if not str(encrypted_data):
        print encrypted_data.stderr
    return str(encrypted_data)

def decrypt_string(encrypted_string, address):
    gpg = gnupg.GPG(gnupghome=os.getcwd()+"/my_keys/gpg_"+address)
    decrypted_data = gpg.decrypt(encrypted_string, always_trust=True)
    return str(decrypted_data.data)

def json_custom_parser(obj):
    """
        A custom json parser to handle json.dumps calls properly for Decimal and Datetime data types.
    """
    if isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        dot_ix = 19 # 'YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM'.find('.')
        return obj.isoformat()[:dot_ix]
    else:
        raise TypeError(obj)