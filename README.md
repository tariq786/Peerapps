PeerApps ALPHA v0.2.1 [[Frontend Repo]](https://github.com/Peerapps/Peerapps-Frontend)
===

[![Tip Balance For Commits](http://peer4commit.com/projects/148.svg)](http://peer4commit.com/projects/148)

 - PeerApps is a data application framework built on the Peercoin blockchain.
 - Learn more about our individual modules (PeerMessage, PeerBlog, etc) by going to the modules/ directory and scoping their READMEs.
 - Learn more about Peercoin from [here](http://peercoin.net/), and check out our forums at [Peercointalk](http://peercointalk.org/).
 - NOTE! We are currently in ALPHA. As such, this application should only be used on Peercoin's testnet, and no binaries will be released.

## Installation Process

### Install Python 2.7.X
 - [Link](https://www.python.org/download/releases/2.7.8/)

### Install wxPython
 - [Link](http://www.wxpython.org/download.php)
 - Alternatively:
    ```
    sudo pip install --upgrade --pre -f http://wxpython.org/Phoenix/snapshot-builds/ wxPython_Phoenix
    ```

### Install OpenSSL
OSX
 - Install [homebrew package manager](http://brew.sh/)
 - ``` $ brew install openssl ```

Windows
 - Install [OpenSSL](http://slproweb.com/download/Win32OpenSSL-1_0_1L.exe)
 - Get an error regarding Visual C++ 2008 Redistributables? [Install this first](http://www.microsoft.com/downloads/details.aspx?familyid=9B2DA534-3E03-4391-8A4D-074B9F2BC1BF)

### Install PIP
OSX
 - ``` $ sudo easy_install pip ```

Windows
 - [Follow this guide](http://stackoverflow.com/questions/4750806/how-to-install-pip-on-windows/12476379#12476379)

### Install Dependencies
OSX
 - ``` $ sudo pip install -r requirements.txt ```

Windows
 - ``` C:\Python27\Scripts\pip.exe install -r requirements.txt ```

### Run the app like a standard client
 - ``` $ python peerapps.py ```
 - This runs the django app as a cherrypy server, and spawns a thread in the background that scans the blockchain and watches the network.

### Run the app for development
 - ``` $ python manage.py runserver 8011 ```
 - This runs the django app using django's built in webserver. This will automatically reload the server for each code change you make, making development easier. On the downside, the blockchain is not being scanned in a background thread.

### Building binaries
 - OSX: ``` python freeze.py py2app ```
 - Windows: ``` python freeze.py py2exe ```

## Changelog

### v0.2.1 [May 2st, 2015]

* Worked on OSX binary build. Everything should work now in the build process, save for some runtime errors with GPG key folders.
* Made source code public.

### v0.2.0 [May 1st, 2015]

* Rewrote framework to use django instead of flask/sqlalchemy, allows better separation of modules.
* Changed opcode "msg" payload to be a json string that includes GPG pub key of sender, instead of just being the message. Ensures each user's GPG pub key gets refreshed into the system with each message they send. Clients download messages to retrieve GPG pub keys if they haven't seen a user's pub key in 1000 blocks (one week).
* Changed framework to point to Peercoin blockchain, and automatically detects if testnet or mainnet

### v0.1.0 [Feb 1st, 2015]

* App published in private alpha off Bitcoin blockchain.
