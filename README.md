PeerApps
===

 - PeerApps is a data application framework built on the Peercoin blockchain.
 - Learn more about our individual modules (PeerMessage, PeerBlog, etc) by going to the modules/ directory and scoping their READMEs.
 - Learn more about Peercoin from [here](http://peercoin.net/), and check out our forums at [Peercointalk](http://peercointalk.org/).
 - NOTE! We are currently in BETA. We are using the Bitcoin blockchain for testing until op_return/bitcoin 0.8 gets merged into Peercoin. This app will not currently work with Peercoin. Even though the app uses the the text "Peercoin" in several places, we are actually using Bitcoin.
 - Check the "Issues" tab to see the next several things I'll be working on.

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

### Run the app
 - ``` $ python peerapps.py ```


## Changelog

### v0.1.0

* App published in private beta off Bitcoin blockchain.
