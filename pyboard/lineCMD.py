"""
Clase para mostrar comandos en una sola linea
"""

class LineCMD(object):
    
    
    def __init__(self,parent, label="",pos=(0,0), width=100):
        self._x,self._y= pos
        self._width=width
        # indice del caracter editado
        self._ic=len(label)
        self._label=label
        self._stctxCmd=wx.StaticText(parent, label=label, pos=pos)
        
    def SetForegroundColour(self, colour):
        self._stctxCmd.SetForegroundColour(colour)
        
    
    def GetLabel(self):
        return self._stctxCmd.GetLabel()
        
    def SetLabel(self,label):
        
        self._stctxCmd.SetLabel(label) #
