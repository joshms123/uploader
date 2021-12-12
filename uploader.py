import audio_input
from threading import Thread
import webbrowser
from tweak import Config
import os.path as path
import sys
import urllib
import application

import requests
import wx

# Globals

audio=audio_input.AudioInput()


class AudioUploader(wx.Frame):
	"""Application to allow uploading of audio files to SndUp"""
	def __init__(self, title):
		self.recording=False
		wx.Frame.__init__(self, None, title=title, size=(350,200)) # initialize the wx frame
		# load config.
		self.config = Config(name="uploader", autosave=True)
		# window events and controls
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.panel = wx.Panel(self)
		self.main_box = wx.BoxSizer(wx.VERTICAL)
		self.select_file = wx.Button(self.panel, -1, "&Select File")
		self.select_file.Bind(wx.EVT_BUTTON, self.SelectFile)
		self.main_box.Add(self.select_file, 0, wx.ALL, 10)
		self.record = wx.Button(self.panel, -1, "&Record")
		self.record.Bind(wx.EVT_BUTTON, self.Record)
		self.main_box.Add(self.record, 0, wx.ALL, 10)
		self.link_label = wx.StaticText(self.panel, -1, "Audio &link")
		self.link = wx.TextCtrl(self.panel, -1, "",style=wx.TE_READONLY)
		self.link.SetValue("Waiting for audio...")
		self.main_box.Add(self.link, 0, wx.ALL, 10)
		self.upload = wx.Button(self.panel, -1, "&Upload")
		self.upload.Bind(wx.EVT_BUTTON, self.OnUpload)
		self.main_box.Add(self.upload, 0, wx.ALL, 10)
		self.upload.Hide()
		self.new = wx.Button(self.panel, -1, "&Attach another file")
		self.new.Bind(wx.EVT_BUTTON, self.Reset)
		self.main_box.Add(self.new, 0, wx.ALL, 10)
		self.new.Hide()
		self.close = wx.Button(self.panel, wx.ID_CLOSE, "&Close")
		self.close.Bind(wx.EVT_BUTTON, self.OnClose)
		self.main_box.Add(self.close, 0, wx.ALL, 10)
		self.panel.Layout()

	def OnUpload(self,event):
		self.UploadThread = Thread(target=self.StartUpload)
		self.UploadThread.start()

	def StartUpload(self):
		"""Starts an upload; only runs after a standard operating system find file dialog has been shown and a file selected"""
		self.select_file.Hide()
		self.upload.Hide()
		self.record.Hide()
		self.link.Show()
		self.link.SetFocus()
		r=requests.post("https://www.sndup.net/post.php", files={"file":open(audio.filename,'rb')})
		try:
			self.link.SetValue(handle_URL(r.json()))
			self.new.Show()
		except:
			self.link.SetValue("Error: "+str(r.text))
			self.new.Show()

	def Record(self,event):
		if self.recording==False:
			audio.start_recording()
			self.record.SetLabel("&Stop")
			self.select_file.Hide()
			self.upload.Hide()
			self.recording=True

		elif self.recording==True:
			audio.stop_recording()
			self.record.SetLabel("&Record")
			self.select_file.Show()
			self.upload.Show()
			self.recording=False
			audio.is_recording=True

	def SelectFile(self,event):
		"""Opens a standard OS find file dialog to find an audio file to upload"""
		openFileDialog = wx.FileDialog(self, "Select the audio file to be uploaded", "", "", "Audio Files (*.mp3, *.ogg, *.wav, *.flac, *.opus)|*.mp3; *.ogg; *.wav; *.flac; *.opus", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if openFileDialog.ShowModal() == wx.ID_CANCEL:
			return False
		audio.filename= openFileDialog.GetPath()
		audio.name=path.basename(audio.filename)
		if audio.is_recording==True:
			audio.cleanup()

		self.upload.Show()

	def Reset(self, event):
		self.record.Show()
		self.upload.Hide()
		self.new.Hide()
		self.select_file.Show()
		self.select_file.SetFocus()
		self.link.ChangeValue("")
		if audio.is_recording==True:
			audio.cleanup()

	def OnClose(self, event):
		"""App close event handler"""
		if audio.is_recording==True:
			audio.cleanup()
		self.Destroy()

def handle_URL(url):
	"""Properly converts an escaped URL to a proper one, taking into account the difference in python 2 and python 3"""
	# We are passed a python dict by default, as SndUp's response is json and we convert that to a dict with .json()
	# So extract the URL from the dict:
	url = url['url']
	final_url = urllib.parse.unquote(url)
	return final_url

def ask(parent=None, message='', default_value=''):
	"""Simple dialog to get a response from the user"""
	dlg = wx.TextEntryDialog(parent, message)
	dlg.ShowModal()
	result = dlg.GetValue()
	dlg.Destroy()
	return result


app = wx.App(redirect=False)
window=AudioUploader(application.name+" "+application.version)
window.Show()
app.MainLoop()