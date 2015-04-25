from bitcoinrpc.authproxy import AuthServiceProxy as rpcRawProxy
import webbrowser
import wx
import thread
import time
import sys
import os
sys.path.append('./')

#clear out pyc files
#find . -name '*.pyc' -delete

os.environ['DJANGO_SETTINGS_MODULE'] = 'peerapps.settings'
import django
django.setup()
import helpers, blockchain_func

class mainFrame(wx.Frame):
    global settings
    def __init__(self, parent, id, title):
        style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER
        self.window = wx.Frame.__init__(self, parent, id, title, size=(450,555), style=style)

        self.tskic = MyTaskBarIcon(self)
        self.statusConnected()

        self.Bind(wx.EVT_CLOSE,self.OnClose)

        wx.GetApp().Bind(wx.EVT_QUERY_END_SESSION, self.onFullClose)
        wx.GetApp().Bind(wx.EVT_END_SESSION, self.onFullClose)
        self.Bind(wx.EVT_CLOSE, self.onFullClose)

        wx.CallAfter(self.StartAsyncThreads)
        self.Layout()

    def statusDisconnected(self):
        icon1 = wx.Icon("frontend/static/images/peerapps_disconnected.png", wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon1)
        self.tskic.statusDisconnected()

    def statusConnected(self):
        icon1 = wx.Icon("frontend/static/images/peerapps_disconnected.png", wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon1)
        self.tskic.statusConnected()

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

        myimage = wx.Bitmap('frontend/static/images/peerapps.png', wx.BITMAP_TYPE_PNG)
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

    def statusDisconnected(self):
        myimage = wx.Bitmap('frontend/static/images/peerapps_disconnected.png', wx.BITMAP_TYPE_PNG)
        submyimage = myimage.GetSubBitmap(wx.Rect(0,0,16,16))
        myicon = wx.EmptyIcon()
        myicon.CopyFromBitmap(submyimage)
        self.SetIcon(myicon, 'PeerApps')

    def statusConnected(self):
        myimage = wx.Bitmap('frontend/static/images/peerapps.png', wx.BITMAP_TYPE_PNG)
        submyimage = myimage.GetSubBitmap(wx.Rect(0,0,16,16))
        myicon = wx.EmptyIcon()
        myicon.CopyFromBitmap(submyimage)
        self.SetIcon(myicon, 'PeerApps')

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
        webbrowser.open("http://127.0.0.1:8011/")

    def GoToPeerMessage(self, event):
        webbrowser.open("http://127.0.0.1:8011/peermessage/")

    def GoToPeerBlog(self, event):
        webbrowser.open("http://127.0.0.1:8011/peerblog/")

    def GoToPeercoinTalk(self, event):
        webbrowser.open("http://www.peercointalk.org/")

class MyApp(wx.App):
    def OnInit(self):
        self.wxPeerApps = mainFrame(None, -1, 'PeerApps')
        return True

    def onCloseIt(self, event):
        for w in wx.GetTopLevelWindows():
            w.Destroy()
        self.Destroy()

def start_webserver():
    from cherrypy import wsgiserver
    import django.core.handlers.wsgi
    server = wsgiserver.CherryPyWSGIServer(
        ('127.0.0.1', 8011),
        django.core.handlers.wsgi.WSGIHandler(),
        server_name='www.django.peerapps',
        numthreads = 5,
    )

    webbrowser.open("http://127.0.0.1:8011/")
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()

def scan_blockchain():
    """
        Scan one block in the blockchain (and mempool as well)
    """
    rpc_raw = rpcRawProxy(helpers.get_rpc_url())
    while True:
        try:
            latest_block, blocks_left = blockchain_func.scan_block(rpc_raw)
            app.wxPeerApps.statusConnected()
            if latest_block:
                print "On the latest block, sleeping for 10 seconds"
                time.sleep(10)
        except:
            app.wxPeerApps.statusDisconnected()
        time.sleep(2)


app = MyApp(0)
app.MainLoop()
