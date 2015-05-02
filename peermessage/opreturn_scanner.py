import os
import external_db
import helpers
import shutil
from models import GPGKey, Spamlist, Message
import json

def save_message(rpc_raw, op_return_data, from_user_address, block_index, tx_id, block_time, msg):

    try:
        verified_message = helpers.verify_and_strip_signature(rpc_raw, msg, from_user_address)
    except AssertionError:
        print "Signature invalid, skip message."
        return
    except AttributeError:
        print "Unable to pull message from external data source."
        return

    #gather my private GPG keys
    my_addresses = []
    for name in os.listdir("./my_keys/"):
        if "gpg_" in name:
            my_addresses.append(name.replace("gpg_", ""))

    #cycle through my private GPG keys attempting decryption
    for to_user_address in my_addresses:
        dec_message = helpers.decrypt_string(verified_message, to_user_address)
        if dec_message:
            new_msg = Message(**{
                "address_from": from_user_address,
                "address_to": to_user_address,
                "block_index": block_index,
                "tx_id": tx_id,
                "msg": dec_message.decode('utf8'),
                "key": op_return_data[5:],
                "time": block_time
            })
            new_msg.save()
            break

def save_gpg_key(rpc_raw, op_return_data, from_user_address, block_index, tx_id, block_time, public_key_string):

    try:
        verified_public_key = helpers.verify_and_strip_signature(rpc_raw, public_key_string, from_user_address)
    except AssertionError:
        print "Signature invalid, skip public key."
        return

    #delete existing from hard drive
    shutil.rmtree('/public_keys/gpg_'+from_user_address, ignore_errors=True)

    #save new to hard drive
    helpers.save_public_key(from_user_address, verified_public_key)

    #delete existing from database
    GPGKey.objects.filter(address=from_user_address).delete()

    #check to see if this is a pub key that is mine. If so, flag it appropriately
    my_addresses = set([a['address'] for a in rpc_raw.listunspent(0)])
    
    #insert new into database
    new_pub_key = GPGKey(**{
        "address": from_user_address,
        "block_index": block_index,
        "tx_id": tx_id,
        "key": op_return_data[5:],
        "time": block_time,
        "mine": True if from_user_address in my_addresses else False
    })
    new_pub_key.save()

def parse(rpc_raw, op_return_data, from_user_address, block_index, tx_id, block_time):
        if op_return_data[2:5] == "pka": #Public Key Announcement
            if not GPGKey.objects.filter(key=op_return_data[5:]).first():
                found_data = external_db.get_data(op_return_data[5:])
                if found_data:
                    print "Found public key"
                    format_public_key = helpers.format_incoming(found_data)
                    save_gpg_key(rpc_raw, op_return_data, from_user_address, block_index, tx_id, block_time, format_public_key)

        elif op_return_data[2:5] == "msg": #Encrypted Message + Public Key
            
            if not Message.objects.filter(key=op_return_data[5:]).exists() or \
                not GPGKey.objects.filter(address=from_user_address, block_index__lt=block_index-1000).exists():
                #If we haven't scanned this message before, or if we do not have a GPGKey from the user within the last 1000 blocks

                if not Spamlist.objects.filter(address=from_user_address).first():
                    #If user isn't on our spam list

                    found_data = external_db.get_data(op_return_data[5:])
                    if found_data:
                        try:
                            formatted_json = json.loads(helpers.format_incoming(found_data))
                        except:
                            return

                        save_message(rpc_raw, op_return_data, from_user_address, block_index, tx_id, block_time, formatted_json['msg'])
                        save_gpg_key(rpc_raw, op_return_data, from_user_address, block_index, tx_id, block_time, formatted_json['pub_key'])
