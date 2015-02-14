import json
import helpers, blockchain_func
from bitcoinrpc.authproxy import AuthServiceProxy as rpcRawProxy
import local_db
import webbrowser
import os
import wx
import thread
import time
from bottle import static_file, redirect, Bottle
import sys
sys.path.append('./')

#clear out pyc files
#find . -name '*.pyc' -delete

class mainFrame(wx.Frame):
    global settings
    def __init__(self, parent, id, title):
        style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER
        self.window = wx.Frame.__init__(self, parent, id, title, size=(450,555), style=style)

        icon1 = wx.Icon("static/images/peercoin.png", wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon1)

        self.tskic = MyTaskBarIcon(self)

        self.Bind(wx.EVT_CLOSE,self.OnClose)

        wx.GetApp().Bind(wx.EVT_QUERY_END_SESSION, self.onFullClose)
        wx.GetApp().Bind(wx.EVT_END_SESSION, self.onFullClose)
        self.Bind(wx.EVT_CLOSE, self.onFullClose)

        wx.CallAfter(self.StartAsyncThreads)
        self.Layout()

    def onFullClose(self, event):
        for w in wx.GetTopLevelWindows():
            w.Destroy()
        self.Destroy()

    def OnClose(self,event):
        self.Show(False)
        event.Veto()

    def StartAsyncThreads(self):
        thread.start_new_thread(start_webserver, ())
        thread.start_new_thread(scan_blockchain, ())

class MyTaskBarIcon(wx.TaskBarIcon):
    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)

        self.frame = frame

        myimage = wx.Bitmap('static/images/peercoin.png', wx.BITMAP_TYPE_PNG)
        submyimage = myimage.GetSubBitmap(wx.Rect(0,0,16,16))
        myicon = wx.EmptyIcon()
        myicon.CopyFromBitmap(submyimage)
        self.SetIcon(myicon, 'PeerApps')
        self.Bind(wx.EVT_MENU, self.GoToSetup, id=1)
        self.Bind(wx.EVT_MENU, self.GoToPeerMessage, id=2)
        self.Bind(wx.EVT_MENU, self.GoToPeerBlog, id=3)
        self.Bind(wx.EVT_MENU, self.GoToPeercoinTalk, id=4)

        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=5)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.OnLeftClick)

    def OnTaskBarClose(self, event):
        self.RemoveIcon()
        self.frame.Destroy()
        for w in wx.GetTopLevelWindows():
            w.Destroy()

    def OnLeftClick(self, e):
        self.PopupMenu(self.CreatePopupMenu())

    def CreatePopupMenu(self):
        tbmenu = wx.Menu()
        tbmenu.Append(1, 'Setup')
        tbmenu.Append(2, 'PeerMessage')
        tbmenu.Append(3, 'PeerBlog')
        tbmenu.Append(4, 'PeercoinTalk (online forums)')
        tbmenu.Append(5, 'Exit')
        return tbmenu

    def GoToSetup(self, event):
        webbrowser.open("http://127.0.0.1:8011/setup")

    def GoToPeerMessage(self, event):
        webbrowser.open("http://127.0.0.1:8011/peermessage")

    def GoToPeerBlog(self, event):
        webbrowser.open("http://127.0.0.1:8011/peerblog")

    def GoToPeercoinTalk(self, event):
        webbrowser.open("http://www.peercointalk.org/")

class MyApp(wx.App):
    def OnInit(self):
        mainFrame(None, -1, 'PeerApps')
        return True

    def onCloseIt(self, event):
        for w in wx.GetTopLevelWindows():
            w.Destroy()
        self.Destroy()

def start_webserver():
    rootApp = Bottle()

    @rootApp.route('/blockchain_scan_status', method='POST')
    def blockchain_scan_status():
        local_db_session = local_db.get_session()
        rpc_raw = rpcRawProxy(helpers.get_rpc_url())
        latest_block, blocks_left = blockchain_func.get_blockchain_scan_status(rpc_raw, local_db_session)
        return json.dumps({
            "status":"success",
            "latest_block": latest_block,
            "blocks_left": blocks_left
        })

    @rootApp.route('/')
    def base():
        redirect("/setup")

    @rootApp.route('/static/:filename#.*#')
    def send_static(filename):
        return static_file(filename, root='./static/')

    for name in os.listdir("./modules/"):
        if os.path.isfile("./modules/"+name+"/server.py"):
            exec "from modules."+name+".server import moduleApp as "+name+"_moduleApp" in globals(), locals()
            rootApp.merge(locals()[name+"_moduleApp"])

    rootApp.run(host='127.0.0.1', port=8011, server='cherrypy')

def scan_blockchain():
    """
        Scan one block in the blockchain (and mempool as well)
    """
    local_db_session = local_db.get_session()
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())
    while True:
        latest_block, blocks_left = blockchain_func.scan_block(rpc_raw, local_db_session)
        if blocks_left == 0:
            print "On the latest block, sleeping for 10 seconds"
            time.sleep(10)


local_db.setup()
app = MyApp(0)
app.MainLoop()
