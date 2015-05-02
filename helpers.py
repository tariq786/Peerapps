import os
import gnupg #also install https://gpgtools.org/gpgsuite.html
import urllib
import datetime
from decimal import Decimal
import platform
from bitcoinrpc.authproxy import AuthServiceProxy
import external_db
import time
import peerapps.settings

import shutil

def download_blg(rpc_raw, key, from_address):
    found_data = external_db.get_data(key)

    if not found_data:
        print "Unable to retrieve blog post, skipping"
        return None

    formatted_message = format_incoming(found_data)
    try:
        verified_message = verify_and_strip_signature(rpc_raw, formatted_message, from_address)
    except AssertionError:
        print "Signature invalid, skip blog post."
        return None
    except AttributeError:
        print "Unable to pull blog post from external data source."
        return None

    return verified_message


def download_blgs(rpc_raw):
    from peerblog.models import Subscription, Blog
    db_blogs = Blog.objects.filter(msg="").order_by('-time')
    my_addresses = [x['address'] for x in rpc_raw.listunspent(0)]
    for b in db_blogs:
        if b.address_from in my_addresses or Subscription.objects.filter(address=b.address_from).exists():
            blog_post = download_blg(rpc_raw, b.key, b.address_from)
            if blog_post is None:
                #delete it or something.
                pass

            print "Saved new blog message", blog_post
            Blog.objects.filter(key=b.key).update(msg=blog_post)

def get_service_status():
    """
        Retrieve user configuration, and status of wallet's rpc server, transaction index, and gpg's installation.
    """
    conf = get_config()
    if 'rpcpassword' in conf and conf['rpcpassword']:
        conf['rpcpassword'] = "*******"

    try:
        rpc_raw = AuthServiceProxy(get_rpc_url())
        rpc_raw.getblockcount()
        conf['wallet_connected_status'] = "good"
    except:
        conf['wallet_connected_status'] = "bad"

    try:
        if not os.path.exists(peerapps.settings.BASE_DIR+"/test_gpg_setup"):
            os.mkdir(peerapps.settings.BASE_DIR+"/test_gpg_setup")
        gnupg.GPG(gnupghome=peerapps.settings.BASE_DIR+"/test_gpg_setup")
        shutil.rmtree(peerapps.settings.BASE_DIR+"/test_gpg_setup", ignore_errors=True)
        conf['gpg_suite_installed'] = "good"
    except:
        conf['gpg_suite_installed'] = "bad"

    return conf

def edit_config(forced_updates, optional_updates=None):
    if platform.system() == 'Darwin':
        btc_conf_file = os.path.expanduser('~/Library/Application Support/PPCoin/')
    elif platform.system() == 'Windows':
        btc_conf_file = os.path.join(os.environ['APPDATA'], 'PPCoin')
    else:
        btc_conf_file = os.path.expanduser('~/.ppcoin')
    btc_conf_file = os.path.join(btc_conf_file, 'ppcoin.conf')

    new_file_contents = ""

    # Extract contents of ppcoin.conf to build service_url
    with open(btc_conf_file, 'r') as fd:
        # PPCoin Core accepts empty rpcuser, not specified in btc_conf_file
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
        new_file_contents += "\n"
        for k,v in forced_updates.items():
            new_file_contents += k + "=" + v + "\n"
        if optional_updates:
            for k,v in optional_updates.items():
                new_file_contents += k + "=" + v + "\n"

    with open(btc_conf_file, 'w') as fd:
        fd.write(new_file_contents)

def get_config():
    if platform.system() == 'Darwin':
        btc_conf_file = os.path.expanduser('~/Library/Application Support/PPCoin/')
    elif platform.system() == 'Windows':
        btc_conf_file = os.path.join(os.environ['APPDATA'], 'PPCoin')
    else:
        btc_conf_file = os.path.expanduser('~/.ppcoin')
    btc_conf_file = os.path.join(btc_conf_file, 'ppcoin.conf')

    # Extract contents of ppcoin.conf to build service_url
    with open(btc_conf_file, 'r') as fd:
        # PPCoin Core accepts empty rpcuser, not specified in btc_conf_file
        conf = {'rpcuser': ""}
        for line in fd.readlines():
            if '#' in line:
                line = line[:line.index('#')]
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            conf[k.strip()] = v.strip()

        conf['rpcport'] = int(conf.get('rpcport', -1))
        conf['rpcssl'] = conf.get('rpcssl', '0')

        if conf['rpcssl'].lower() in ('0', 'false'):
            conf['rpcssl'] = False
        elif conf['rpcssl'].lower() in ('1', 'true'):
            conf['rpcssl'] = True
        else:
            raise ValueError('Unknown rpcssl value %r' % conf['rpcssl'])

    if conf['rpcport'] == -1:
        if 'testnet' in conf and conf['testnet'] in ['1', 'true']:
            conf['rpcport'] = 9904
        else:
            conf['rpcport'] = 9902

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

def get_pk(address):
    if not os.path.isdir(peerapps.settings.BASE_DIR+"/my_keys/gpg_"+address):
        raise ValueError
    gpg = gnupg.GPG(gnupghome=peerapps.settings.BASE_DIR+"/my_keys/gpg_"+address)
    return gpg.export_keys(gpg.list_keys()[0]['keyid'])

def check_gpg_status(address):
    return os.path.isdir(peerapps.settings.BASE_DIR+"/my_keys/gpg_"+address)

def save_public_key(address, key):
    pk_dir = peerapps.settings.BASE_DIR+"/public_keys/gpg_"+address+'/'
    shutil.rmtree(pk_dir, ignore_errors=True)
    os.makedirs(pk_dir)
    with open(pk_dir+'keys.asc', 'w') as f:
        f.write(key)

def setup_gpg(address):
    if not os.path.exists(peerapps.settings.BASE_DIR+"/my_keys/gpg_"+address):
        os.mkdir(peerapps.settings.BASE_DIR+"/my_keys/gpg_"+address)
    gpg = gnupg.GPG(gnupghome=peerapps.settings.BASE_DIR+"/my_keys/gpg_"+address)
    input_data = gpg.gen_key_input(name_email=address+'@peercoin.net')
    key = gpg.gen_key(input_data)
    ascii_armored_public_keys = gpg.export_keys(str(key))
    ascii_armored_private_keys = gpg.export_keys(str(key), True)
    with open(peerapps.settings.BASE_DIR+"/my_keys/gpg_"+address+'/keys.asc', 'w') as f:
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
    gpg = gnupg.GPG(gnupghome=peerapps.settings.BASE_DIR+"/public_keys/gpg_"+address)
    key_data = open(peerapps.settings.BASE_DIR+"/public_keys/gpg_"+address+'/keys.asc').read()
    gpg.import_keys(key_data)
    encrypted_data = gpg.encrypt(plaintext, address+'@peercoin.net', always_trust=True)
    if not str(encrypted_data):
        print encrypted_data.stderr
    return str(encrypted_data)

def decrypt_string(encrypted_string, address):
    gpg = gnupg.GPG(gnupghome=peerapps.settings.BASE_DIR+"/my_keys/gpg_"+address)
    decrypted_data = gpg.decrypt(encrypted_string, always_trust=True)
    return str(decrypted_data.data)

def json_custom_parser(obj):
    """
        A custom json parser to handle json.dumps calls properly for Decimal and Datetime data types.
    """
    if isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        return time.mktime(obj.timetuple())
    else:
        raise TypeError(obj)