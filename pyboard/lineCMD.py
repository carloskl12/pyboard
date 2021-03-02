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
        # indice de caracter offset izquierdo
        self._icoleft=0
        # indice de caracter offset derecho
        self._icoright=self._ic
        self._label=""
        self._stctxCmd=wx.StaticText(parent, label=layout, pos=pos)
        
        # Historial
        self._hist=[]
        self._ih=0 #índice del historial

    @property
    def label(self):
        return self._label
    
    @property
    def historialIndex(self):
        return self._ih
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def SetForegroundColour(self, colour):
        self._stctxCmd.SetForegroundColour(colour)
        self._fgColour= colour
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def GetLabel(self):
        return self._stctxCmd.GetLabel()
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def SetLabel(self,label):
        s= self._layout+label
        self._label=label
        self._ic=len(label)
        self.UpdateCMDstate()

    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def KeyInput(self,keyCode, unicodeKey):
        """
        Interpreta una entrada del teclado segun el estado 
        de la linea de comando. Si es un caracter válido, lo añade 
        al texto mostrado o cambia si el índice de caracter indica 
        que no está en la posición final
        
        keyCode: codigo de teclado
        unicodeKey: valor unicode interpretado
        """
        if unicodeKey == 13:# Intro
            if self._label != '':
                self._hist.append(self._label)
            self._ih = 0
            self._ic = 0
            self._label = ''
            print("  **** enter")
        
        elif keyCode == 8:# retroceso (borra un caracter)
            if len(self._label) == 0:
                return
            elif self._ic == len(self._label):
                self._label = self._label[:-1]
                self._ic-=1
            elif self._ic > 0:
                self._ic-=1
                self._label = self._label[:self._ic]+self._label[self._ic+1:]
                
            if self._icoleft >0:
                self._icoleft-=1
        elif keyCode == 127:# delete
            if len(self._label) == 0 or self._ic == len(self._label):
                return
            
            self._label = self._label[:self._ic]+self._label[self._ic+1:]
            if self._icoleft >0:
                self._icoleft-=1
        elif keyCode in (315,317):# arriba abajo
            if keyCode == 315: # Arriba
                self._ih-=1
            elif keyCode == 317: #abajo
                self._ih+=1
            # longitud del historial
            lenH=len(self._hist)
            
            if self._ih > 0:
                self._ih=0
            elif self._ih< -lenH:
                self._ih=-lenH
            
            else:
                
                if self._label == self._hist[-1] and self._ih == 0 :
                    self._label = ''
                else:
                    self._label = self._hist[self._ih]
                self._ic=len(self._label)
        elif keyCode in (314,316):# izquierda derecha
            if keyCode == 314 and self._ic >= 0:
                if self._icoleft > 0:
                    self._icoleft -= 1
                if self._ic > 0:
                    self._ic -= 1
            elif keyCode == 316 and self._ic < len(self._label):
                self._ic += 1
                if self._icoright < len(self._label):
                    self._icoright += 1
        elif unicodeKey>31:
            if self._ic == len(self._label):
                self._label+=chr(unicodeKey)
            else:
                self._label=self._label[:self._ic]+chr(unicodeKey)+self._label[self._ic:]
                self._icoright+=1
                if self._icoright > len(self._label):
                    self._icoright = len(self._label)
            self._ic+=1
            
        self.UpdateCMDstate()
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def UpdateCMDstate(self):
        """
        Actualiza la barra de comandos con los estados activos
        
        """
        dc = wx.PaintDC(self._parent)
        if self._ic == len(self._label):
            # Caso en que está insertando caracteres al final
            s= self._layout+self._label
            #dc.SelectObject(self._parent)
            wtext,htext=dc.GetTextExtent(s)
            ic=1
            while wtext > self._width:
                wtext,htext=dc.GetTextExtent(self._layout+self._label[ic:])
                ic+=1
            ic-=1
            self._icoleft=ic
            self._icoright=self._ic
            
            # Borra la info anterior
            dc.SetBrush( dc.GetBackground() )
            pen=wx.Pen(dc.GetBackground().GetColour())
            dc.SetPen(pen)
            dc.DrawRectangle(self._x,self._y, self._width, 20)
            pen=wx.Pen("#ffffff", 1, wx.PENSTYLE_CROSS_HATCH )
            dc.SetPen(pen)
            s = self._layout+self._label[self._icoleft:self._icoright]
            dc.DrawText(s,self._x, self._y)

            
        elif self._icoleft <= self._ic < self._icoright:
            # Se tiene una edición en medio del string
            s= self._layout+self._label[self._icoleft:self._icoright]
            wtext,htext=dc.GetTextExtent(s)
            ic=0
            while wtext > self._width:
                if ic%2 == 0 and self._ic +1 < self._icoright :
                    self._icoright-=1
                    s= self._layout+self._label[self._icoleft:self._icoright]
                    wtext,htext=dc.GetTextExtent(s)
                elif ic%2 == 1 and self._icoleft+1 <= self._ic:
                    self._icoleft+=1
                    s= self._layout+self._label[self._icoleft:self._icoright]
                    wtext,htext=dc.GetTextExtent(s)
                else:
                    raise Exception("Error inesperado")
                ic+=1
            
            # Borra la info anterior
            dc.SetBrush( dc.GetBackground() )
            pen=wx.Pen(dc.GetBackground().GetColour())
            dc.SetPen(pen)
            dc.DrawRectangle(self._x,self._y, self._width, 20)
            s=self._layout+self._label[self._icoleft:self._icoright]
            pen=wx.Pen("#ffffff", 1, wx.PENSTYLE_CROSS_HATCH )
            dc.SetPen(pen)
            dc.DrawText(s,self._x, self._y)
            
            # Indicador del caracter actual
            
            s=self._layout+self._label[self._icoleft:self._ic]
            wtext0, htext=dc.GetTextExtent(s)
            
            s=self._layout+self._label[self._icoleft:self._ic+1]
            wtext1, htext=dc.GetTextExtent(s)
            
            if self._ic == 0:
                wtext0=wtext1-5
            # ajuste para dibujar
            pen=wx.Pen("#fce94f", 2, wx.PENSTYLE_CROSS_HATCH )
            dc.SetPen(pen)
            xof,yof =self._x,self._y
            dc.DrawLine((wtext0+xof,yof+17),(wtext1+xof,yof+17))
        else:
            msg="Error en la lógica de los índices de la cadena. "
            msg+=" icoleft=%i, ic=%i, icoRight=%i"%(self._icoleft, self._ic, self._icoright)
            raise Exception(msg)
        
        


