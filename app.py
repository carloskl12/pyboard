import wx

import os, time
from pyboard import DrawZone

class MainFrame(wx.Frame):
  def __init__(self):
    
    # youtube 1280x720 720p
    #minSize=(854,480) #youtube 480p
    
    minSize=(1024,576) # Formato 16/9 unidad a 64
    wx.Frame.__init__(self, None, size=minSize, title="Pyboard")
    
    self.dirs={'tmp':'./resource/tmp',
           'help':'./resource/slides/help',
           'slides':'./resource/slides',
           'chalkboard':'./resource/chalkboard' #donde se guardan los resultados
           }
    # Create a panel and notebook (tabs holder)
    p = DrawZone(self,minSize)
    p.SetBackgroundColour('#e2f99f')
    self.p=p
    self.SetMinSize(minSize)
    self.SetMaxSize(minSize)
    self.Centre()
    #self.sb = self.CreateStatusBar()
    self.Msg('Size:'+str(p.GetSize()))

    self.SetupDirs()
    
    self.Bind(wx.EVT_CLOSE, self.OnExit)

  def MsgTop(self, msg):
    s='Pyboard'
    if msg !='':
      s+=' -- '+msg
    self.SetTitle(s)

  def SetupDirs(self):
    '''
    Verifica si existen los directorios correspondientes para poder iniciar,
    en caso contrario los creará
    '''
    for k, v in self.dirs.items():
      if not os.path.isdir(v):
        os.makedirs(v)
        self.Msg('  Directorio creado: %s'%v)
    
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def OnExit(self,e):
    self.p.Save()
    print('**Cerrado correctamente')
    try:
        self.Destroy()
    except:
        print("fin")

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def Msg(self,texto):
    try:
      self.sb.SetStatusText('>>  '+ texto)
    except:
      pass
    print(texto)
if __name__ == "__main__":
    print('  wx version:',wx.__version__)
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()
