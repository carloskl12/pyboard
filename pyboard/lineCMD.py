"""
Clase para mostrar comandos en una sola linea
"""
import wx

class LineCMD(object):
    """
    parent: padre donde se alojará el texto 
    pos: posición
    width: ancho del texto
    layout: prefijo a mostrar
    
    """
    
    def __init__(self,parent, pos=(0,0), width=100, layout="| >> "):
        self._parent=parent
        self._x,self._y= pos
        self._width=width
        self._layout= layout
        # indice del caracter editado
        self._ic=0
        self._label=""
        self._stctxCmd=wx.StaticText(parent, label=layout, pos=pos)

        
    def SetForegroundColour(self, colour):
        self._stctxCmd.SetForegroundColour(colour)
        
    
    def GetLabel(self):
        return self._stctxCmd.GetLabel()
        
    def SetLabel(self,label):
        s= self._layout+label
        self._label=label
        self._ic=len(label)
        #dc = wx.BufferedPaintDC(self._parent)
        dc = wx.PaintDC(self._parent)
        #dc.SelectObject(self._parent)
        wtext,htext=dc.GetTextExtent(s)
        ic=1
        while wtext > self._width:
            wtext,htext=dc.GetTextExtent(self._layout+label[ic:])
            ic+=1
        ic-=1
        self._stctxCmd.SetLabel(self._layout+label[ic:])
