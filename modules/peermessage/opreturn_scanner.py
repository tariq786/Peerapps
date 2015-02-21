import os
import local_db, external_db
import helpers
import shutil

def parse(rpc_raw, local_db_session, op_return_data, from_user_address, block_index, tx_id, block_time):
    found_data = external_db.get_data(op_return_data[5:])
    if op_return_data[2:5] == "pka": #Public Key Announcement
        if not local_db_session.query(local_db.PublicKey).filter(local_db.PublicKey.key==op_return_data[5:]).first():
            print "Found public key"
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

    elif op_return_data[2:5] == "msg": #Encrypted Message
        if not local_db_session.query(local_db.Message).filter(local_db.Message.key==op_return_data[5:]).first():
            #If we haven't already scanned this message
            if not local_db_session.query(local_db.Ignore).filter(local_db.Ignore.address==from_user_address).first():
                #If user isn't on our spam list
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
                print "Found message"
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
