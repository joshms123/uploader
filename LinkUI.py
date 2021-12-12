import wx
class LinkUI(wx.Dialog):
	def __init__(self, parent, url):
		self.parent=parent
		wx.Dialog.__init__(self, parent, title="URL Ready", size=wx.DefaultSize) # initialize the wx frame
		self.panel = wx.Panel(self)
		self.main_box = wx.BoxSizer(wx.VERTICAL)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.link_label = wx.StaticText(self.panel, -1, "Audio &link")
		self.link = wx.TextCtrl(self.panel, -1, "",style=wx.TE_READONLY)
		self.link.SetValue(url)
		self.main_box.Add(self.link, 0, wx.ALL, 10)
		self.link.SetFocus()
		self.close = wx.Button(self.panel, wx.ID_CANCEL, "&Cancel")
		self.close.Bind(wx.EVT_BUTTON, self.OnClose)
		self.main_box.Add(self.close, 0, wx.ALL, 10)
		self.panel.Layout()
	
	def OnClose(self, event):
#		self.parent.Raise()
#		self.parent.SetFocus()
		self.Destroy()

def ShowLink(parent,url):
	link = LinkUI(parent,url)
	return link.ShowModal()