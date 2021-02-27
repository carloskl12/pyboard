#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import wx, os
import math
from .formulaCtrl import FormulaCtrl
from .utils import getFileList, Slides
from .figure import Figure
from .lineCMD import LineCMD
MODO_COMANDO=0
MODO_TEXTO=1
MODO_FORMULA=2
MODO_DIBUJO=3

TOOL_LAPIZ=0
TOOL_POLIGONO=1
TOOL_GOMA=2
TOOL_CIRCULO=3
TOOL_CUADRADO=4
TOOL_SELEC=5
class DrawZone(wx.Control):
  """
  se espera que exista:
  _startedControl = False: si ya se ha vuelto visible por primera vez
  _widthIZ: ancho de la zona interactiva
  _heightIZ : alto de la zona interactiva
  
  self._visibleGrid
  self._bmpGridCache
  self._bmpDrawCache
  """
  _modos={MODO_COMANDO:'comando (c)',MODO_TEXTO:'texto (t)',
    MODO_FORMULA:'fórmula (f)', MODO_DIBUJO:'dibujo (d)'}
  
  _tools={TOOL_LAPIZ:'lápiz (l)', TOOL_POLIGONO:'polígono (p)',
          TOOL_GOMA:'goma (g)', TOOL_CIRCULO:'círculo (c)',
          TOOL_CUADRADO:'cuadrado (C)',TOOL_SELEC:'selección (S)'}
  
  _ESTILOS={1:{'bgBoardColour': '#113700',
               'drawColour': '#ffffff',
               'sbColour':'#1f1200',
               'sbtxtColour':'#ffffff', },
            2:{'bgBoardColour': '#000000',
               'drawColour': '#ffffff',
               'sbColour':'#1f1200',
               'sbtxtColour':'#ffffff', },
            3:{'bgBoardColour': '#ffffff',
               'drawColour': '#000000',
               'sbColour':'#1f1200',
               'sbtxtColour':'#ffffff', },
           }
  MAX_PEN_WIDTH=100
  def __init__(self,parent, size):
    '''
    
    '''
    super(DrawZone, self).__init__(parent, -1, size=size, style=wx.BORDER_NONE)
    
    ancho, alto = self.DoGetBestSize()
    self.parent=parent
    self._undoActive=False #No hay acción para deshacer
    self._isDrawing=False #Indica si se está realizando un trazo con clic sostenido
    self._isDraggingFigure=False #Indica si se está moviendo una figura
    self._figure=None
    self._selection=None #Figura de tipo rectangulo para indicar la selección
    self._selectionBmp=None #Bmp donde se guarda la selección para poder mover
    self._imodo=0 #Indice de modo
    self.modo=self._modos[self._imodo]
    self._kmodes=[m[-2] for k,m in self._modos.items()]
    self.dirs=parent.dirs
    self._slidesOn=False #Si hay presentación
    self._slides=None #lista de los slides o diapositivas
    self._lastClickLeft=(0,0) #Ultima posición del clic izquierdo
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Ingreso de texto 
    self._txbuff='' #Buffer
    self._txtSize=14
    self._drawTxt=wx.StaticText(self,label='',pos=(0,0))
    self._drawTxt.SetFont(wx.Font( wx.FontInfo(self._txtSize).Family(wx.FONTFAMILY_SWISS) ))
    self._txtHistorial=[] # historial de texto
    self._indexHistorial=0 #Indice para el historial
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Barra de estado
    self.sbHeight=24
    self.sb= wx.Control(self,size=(ancho,self.sbHeight),
      pos=wx.Point(0,alto-self.sbHeight),style=wx.BORDER_NONE)
    self._sbtxModo=wx.StaticText(self.sb, label='Modo: %s'%self.modo, pos=(10,2))
    self._sbtxCmd=LineCMD(self.sb, layout='| >> ', pos=(160,2), width=390)
    self._sbtxInfo=wx.StaticText(self.sb, label='| Msg: ', pos=(560,2))

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # memoria de dibujo para evitar flicker
    self._bmpDrawCache=wx.Bitmap(ancho,alto)
    # para guardar la última modificación del mapa de bits
    self._bmpDrawUndo=wx.Bitmap(ancho,alto) 
    self.SetStyle(1)
    self._lastPoint=None #Se usa para susavizar el dibujado con rectas
    self._lastPoint2=None #Se utiliza para que funcione bien el deshacer en modo poligono
    self._toolDraw=0 #Herramienta de dibujo
    self._penWidth=2 #Herramienta
    self._eraserWidth=24#Ancho del borrador
    dc = wx.MemoryDC()
    dc.SelectObject(self._bmpDrawCache)
    dc.SetBackground(wx.Brush(self._bgBoardColour))
    dc.Clear()
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # formula
    self.formula=FormulaCtrl(self,fsize=24,bcolour=self._bgBoardColour, size=(450,200))

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # varios
    self._startedControl=False
    self.Bind(wx.EVT_PAINT, self.OnPaint)
    self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground) 
    
    self.Bind(wx.EVT_SIZE, self.OnSize)
    
    self.Bind(wx.EVT_KEY_UP, self.OnCommand)
    self.Bind(wx.EVT_CHAR, self.OnChar)
    self.Bind(wx.EVT_LEFT_UP, self.OnLeftClic)
    
    self.Bind(wx.EVT_RIGHT_UP, self.OnRighClic)
    
    #self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)


  @property
  def drawColour(self):
    return self._drawColour
  @drawColour.setter
  def drawColour(self,c):
    self._drawColour=c
    self.formula.fcolour=c
    self._drawTxt.SetForegroundColour(c)

  def SetFont(self, font):
    '''
    Ajusta la fuente de la zona de dibujo, esta es diferente a la de la 
    barra de estado
    '''
    pass

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def SetStyle(self, style=1):
    '''
    Fija el estilo de colores, según el estilo dado, y 
    redibuja el caché según el nuevo color de fondo
    '''
    estilo=self._ESTILOS[style]
    self._bgBoardColour=estilo['bgBoardColour'] #Fondo de la pizarra
    self._drawColour=estilo['drawColour'] #Color para dibujar
    
    if hasattr(self,'formula'):
      #print('  ** si cambia color de fórmula', self._bgBoardColour)
      self.formula.bcolour=self._bgBoardColour
      #print(self.formula.bcolour)
      self.formula.fcolour=self._drawColour
    if self._slides != None:
      self._slides.SetBackgroundColour(self._bgBoardColour)
    
    # Barra de estado
    self.sb.SetBackgroundColour(estilo['sbColour'])
    self._sbtxModo.SetForegroundColour(estilo['sbtxtColour'])
    self._sbtxCmd.SetForegroundColour(estilo['sbtxtColour'])
    self._sbtxInfo.SetForegroundColour(estilo['sbtxtColour'])

    #Formula
    
    # Otros
    self._drawTxt.SetForegroundColour(estilo['drawColour'])
    # Borra con el nuevo color de fondo
    dc = wx.MemoryDC()
    dc.SelectObject(self._bmpDrawCache)
    dc.SetBackground(wx.Brush(self._bgBoardColour))
    dc.Clear()
    #self.DoPaint()
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def GetDir(self, dirDefault, fileExt=None):
    '''
    Obtiene un directorio
    '''
    dlg=None
    if fileExt!=None:
      dlg = wx.FileDialog(self, "Escoger el archivo", dirDefault, "", fileExt, wx.FD_OPEN)
    else:
      dlg = wx.DirDialog(self, defaultPath=dirDefault)
    if dlg.ShowModal() == wx.ID_OK:
      filename,dirname='',''
      if fileExt !=None:
        filename = dlg.GetFilename()
        dirname = dlg.GetDirectory()
      else:
        dirname = dlg.GetPath()
      return (filename, dirname)

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def SetMode(self,modo):
    '''
    Fija el modo de trabajo
    '''
    imodo=self._imodo
    if isinstance(modo, int):
      if not (modo in self._modos):
        raise Exception('Modo no válido: %i'%modo)
      self.modo=self._modos[modo]
      self._imodo=modo
    elif modo in self._kmodes:
      '''
      _kmodes es una lista con las letras respectivas al modo
      '''
      self._imodo=self._kmodes.index(modo)
      self.modo=self._modos[self._imodo]
    else:
      raise Exception('Modo no válido: %s'%str(modo))
    if imodo != self._imodo:
      self._txbuff=''
      self.Cmd()
      
      if self._imodo == MODO_DIBUJO:
        tool=self._tools[self._toolDraw]
        self.parent.MsgTop('Modo: %s -- %s '%(self.modo,tool))
      else:
        self.parent.MsgTop('Modo: %s'%self.modo)
      self._sbtxModo.SetLabel('Modo: %s'%self.modo)
        

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def OnCommand(self,e):
    '''
    Se ejecuta en modo comandos
    '''
    keyCode= e.GetKeyCode()
    if e.ControlDown():
      if keyCode == ord('Z'):
        self.Undo()
        self.Msg('  Deshacer activado')
      return
    
    if self._imodo != MODO_COMANDO:
      if keyCode==9: #Tabulador:
        if self._imodo == MODO_FORMULA:
          self.SetMode('d')
          self.Bind(wx.EVT_MOTION, self.OnDrawing)
          self._isDrawing=False
          self.DropFormula()
          self._txbuff=''
          self.formula('')
          self.Msg(self._tools[self._toolDraw])
        elif self._imodo == MODO_DIBUJO:
          self.Unbind(wx.EVT_MOTION)
          x,y=self._lastClickLeft
          self.DropFigure()
          self.formula.SetPosition((x,y-10))
          self.SetMode('f')
          self.Msg('Modo fórmula activado')
          #self.DoPaint()
      return
    
      
    print('  keyCode:',keyCode)
    if keyCode == 67: #Redundante
      self.SetMode('c')
    elif keyCode == 84:
      self.SetMode('t')
    elif keyCode == 70:
      self.SetMode('f')
    elif keyCode == ord('D'):
      self.SetMode('d')
      self.Bind(wx.EVT_MOTION, self.OnDrawing)
      self._isDrawing=False
    elif keyCode == ord('A'):
      if self._slidesOn:
        #self.SetSlide(self._islide-1)
        slideIndex=self._slides.Previus()
        self.Msg(' anterior (a) -- %i'%(slideIndex+1))
        # Para no colapsar con imágenes del anterior slide
        self._undoActive=False
        self.DoPaint()
    elif keyCode == ord('S'):
      if self._slidesOn:
        #self.SetSlide(self._islide+1)
        slideIndex=self._slides.Next()
        self.Msg(' siguiente (s) -- %i'%(slideIndex+1))
        self._undoActive=False
        self.DoPaint()
      else:
        dlg=wx.MessageDialog(self.parent,"¿Desea activar el modo presentación?", style=wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
          # Inicia el modo presentación
          self._slides=Slides(self.dirs['chalkboard'], self._bmpDrawCache, 
            self._bgBoardColour, self.sbHeight)
          self._slidesOn=True
          print('  **Slides activados')
        else:
          pass
        dlg.Destroy()
    elif keyCode == ord('P'):#activa presentación
      fname, dirname= self.GetDir(self.dirs['slides'])
      basename=os.path.basename(os.path.normpath(dirname))
      if self._slidesOn:
        self._slides.SaveSlide()
      
      self._slides=Slides(self.dirs['chalkboard'], self._bmpDrawCache, 
            self._bgBoardColour, self.sbHeight, name=basename,dirslidesBg=dirname)
      self._slidesOn=True
      self.DoPaint()
    elif keyCode == ord('R'):#Refresca slide de fondo
      if self._slidesOn:
        self._slides.Refresh()
        self.DoPaint()
    elif keyCode == ord('I'):
      if self._slidesOn:
        self._slides.Instert()
        self.DoPaint()
    elif keyCode == ord('1'):
      self.SetStyle(1)
      self.DoPaint()
    elif keyCode == ord('2'):
      self.SetStyle(2)
      self.DoPaint()
    elif keyCode == ord('3'):
      self.SetStyle(3)
      self.DoPaint()

  def Save(self):
    if self._slidesOn:
      self._slides.SaveSlide()

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def OnDrawing(self,e):
    '''
    Mientras se mueve el cursor cuando está en modo dibujo
    '''
    left= e.LeftIsDown()
    right= e.RightIsDown()
    state = wx.GetMouseState()
    
    #print(' arrastra')
    if left or right:
      p = e.GetPosition()
      if state.ShiftDown() and self._lastPoint !=None:
        # Ajusta para las lineas rectas con la herramienta polígono
        x0,y0= self._lastPoint
        x,y=p
        dx,dy=abs(x-x0),abs(y-y0)
        if dx>dy:
          p=(x,y0)
        else:
          p=(x0,y)
        
      rightV=-1
      esTrazoContinuo= self._toolDraw in ( TOOL_GOMA , TOOL_LAPIZ, TOOL_POLIGONO)
      dc = wx.MemoryDC()
      if not self._isDrawing:
        # Se guarda apenas inicia un trazo 
        if esTrazoContinuo:
          self.SaveLastAction(dc)
        if self._figure != None:
          if self._figure.HitTest(p):
            self._isDraggingFigure=True
        elif self._selection != None:
          if self._selection.HitTest(p):
            self._isDraggingFigure=True
            
        if self._isDraggingFigure:
          self._lastPoint=p
        elif self._toolDraw == TOOL_CIRCULO:
          self._lastPoint=p
          self._figure=Figure('circle',p,0)
        elif self._toolDraw == TOOL_CUADRADO: 
          self._lastPoint=p
          self._figure=Figure('rectangle',p,1,1)
        elif self._toolDraw == TOOL_SELEC:  
          self._lastPoint=p
          self.DropSelection()
          self._selection=Figure('rectangle',p,1,1)
          print('  Selección')
      else:
        if self._isDraggingFigure:
          xc,yc= self._lastPoint
          x,y= p
          dx,dy=x-xc,y-yc
          if self._figure !=None:
            xi,yi=self._figure.posIni
            self._figure.pos=(xi+dx,yi+dy)
          elif self._selection !=None:
            xi,yi=self._selection.posIni
            self._selection.pos=(xi+dx,yi+dy)
        elif self._toolDraw == TOOL_CIRCULO:
          xc,yc= self._lastPoint
          x,y= p
          self._figure.radius=round(math.sqrt((x-xc)**2+(y-yc)**2))
        elif self._toolDraw == TOOL_CUADRADO:
          xc,yc= self._lastPoint
          x,y= p
          self._figure.width=x-xc
          self._figure.height=y-yc
        elif self._toolDraw ==TOOL_SELEC:
          xc,yc= self._lastPoint
          x,y= p
          self._selection.width=x-xc
          self._selection.height=y-yc
      self._isDrawing=True
      dc.SelectObject(self._bmpDrawCache)
      
      normalPen=wx.Pen(self._drawColour, self._penWidth, wx.PENSTYLE_CROSS_HATCH )
      eraserPen=wx.Pen(self._bgBoardColour, self._eraserWidth, wx.PENSTYLE_CROSS_HATCH )
      if left and not right:
        rightV=0 
        if self._toolDraw == TOOL_GOMA:
          dc.SetPen(eraserPen)
        else:
          dc.SetPen(normalPen)
      elif right and not left:
        rightV=1
        if self._toolDraw == TOOL_GOMA:
          dc.SetPen(normalPen)
        else:
          dc.SetPen(eraserPen)
      else:
        print('Doble boton LR')
      if rightV>-1:
        if esTrazoContinuo:
          if self._lastPoint == None:
              dc.DrawLine(p,p)
          else:
            dc.DrawLine(self._lastPoint,p)
        #elif self._toolDraw == TOOL_CIRCULO:
        #  self._figure.Draw(dc)
        #print( '  pos:',p)
        # Se guarda el último punto cuando se arrastra para 
        # algunas herramientas que utilizan el trazo continuo
        if esTrazoContinuo:
          self._lastPoint=p
        self.DoPaint()
    else:
      self._isDrawing=False
  

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def Erase(self):
    '''
    Borra todo el contenido
    '''
    self.DropText()
    dc = wx.MemoryDC()
    dc.SelectObject(self._bmpDrawCache)
    dc.SetBackground(wx.Brush(self._bgBoardColour))
    dc.Clear()
    self.Msg('Pizarra borrada')
    self.DoPaint()
    

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def OnChar(self,e):
    keyCode= e.GetKeyCode()
    unicodeKey=e.GetUnicodeKey()
    if self._imodo == 1:
      self.ModeText(keyCode,unicodeKey)
    elif self._imodo == 3:
      self.ModeDraw(keyCode,unicodeKey)
    elif self._imodo == 2:
      self.ModeFormula(keyCode,unicodeKey)
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def ModeText(self, keyCode, unicodeKey):
    '''
    Entrada de texto en modo texto
    '''
    if keyCode==27:
      self.SetMode(0)
      self.DropText()
      return
    if unicodeKey == 13:
      self.DropText()
      # Calcula la siguiente linea
      w,h=self._drawTxt.GetSize()
      x,y= self._drawTxt.GetPosition()
      self._drawTxt.SetPosition( (x,y+h))
      self.DoPaint()
    elif unicodeKey == 8:
      self._txbuff=self._txbuff[:-1]
    elif unicodeKey>31:
      self._txbuff+=chr(unicodeKey)
    
    self._drawTxt.SetLabel(self._txbuff)
    self.Cmd(self._txbuff)
    self.Msg('keyCode - %i'%keyCode)

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def ModeFormula(self, keyCode, unicodeKey):
    '''
    Entrada de texto en modo texto
    '''
    if keyCode==27:
      # Escape
      self.SetMode(0)
      self.DropFormula()
      self._txbuff=''
      self.formula('')
      self.DoPaint()
      #self.Unbind(wx.EVT_MOTION)
      return
    if unicodeKey == 13:
      #Nueva linea
      self.DropFormula()
      w,h=self.formula.textSize
      # Agrega al historial
      if self._txbuff!='':
        self._txtHistorial.append(self._txbuff)
      self._indexHistorial=0
      self._txbuff=''
      self.formula('')
      
      x,y= self.formula.GetPosition()
      self.formula.SetPosition( (x,y+h))
      #self.DoPaint()
    elif unicodeKey == 8:
      #Borrar un caracter
      self._txbuff=self._txbuff[:-1]
    elif keyCode in (315,317):
      #314,315,316,317 Izquierda, arriba, derecha, abajo
      self.Msg("historial - %i"%((-1)*self._indexHistorial))
      if keyCode == 315: # arriba
        # sube en el historial
        self._indexHistorial-=1
      elif keyCode == 317: #abajo
        self._indexHistorial+=1
      
      if self._indexHistorial > 0:
        self._txbuff=''
        self._indexHistorial=0
      else:
        try:
          self._txbuff = self._txtHistorial[self._indexHistorial]
        except:
          self._txbuff=''
          self._indexHistorial=0
    elif unicodeKey>31:
      self._txbuff+=chr(unicodeKey)
    
    self.formula(self._txbuff)
    self.Cmd(self._txbuff)
    self.DoPaint()
    #self.Msg('keyCode - %i'%keyCode)
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def ModeDraw(self, keyCode, unicodeKey):
    '''
    Entrada de texto en modo dibujo
    '''
    if keyCode==27:
      self.SetMode(MODO_COMANDO)
      
      self.Unbind(wx.EVT_MOTION)
      self.DropFigure()
      self.DropSelection()
      self._lastPoint=None
      return
    lastTool=self._toolDraw
    lastColour=self.drawColour
    if keyCode == ord('f'):#Finaliza una linea se usa para modo poligono
      self._lastPoint=None
      if self._figure != None:
        self.Msg(self._figure.tipo)
        self.DropFigure()
      elif self._selection != None:
        if self._selectionBmp != None:
          self.DropSelection()
        else:
          self.ClipSelection()
      else:
        self.Msg('Fin de linea')
    elif keyCode == ord('F'):
      # utilizado explicitamente para realizar una copia
      # ya sea de la figura o la selección actual
      self._lastPoint=None
      if self._figure != None:
        self.Msg(self._figure.tipo)
        self.DropFigure(True)
      elif self._selection != None:
        if self._selectionBmp != None:
          self.DropSelection(True)
        else:
          self.ClipSelection(True)
      else:
        self.Msg('Fin de linea')
    elif keyCode == ord('p'):#Activa modo polígono
      self._toolDraw=TOOL_POLIGONO
      self.Msg('poligono activado (p)')
    elif keyCode == ord('e'):#Activa modo polígono
      #self._toolDraw=1
      if self._toolDraw != TOOL_SELEC:
        self.Erase()
        self.Msg('eliminar todo (e)')
      else:
        self.EraseSelection()
        self.Msg('eliminada la selección (e)')
    elif keyCode == ord('l'):#Activa modo lápiz
      self._toolDraw=TOOL_LAPIZ
      self._lastPoint=None
      self.Msg('lápiz activado (l)')
    elif keyCode == ord('g'):#Activa modo lápiz
      self._toolDraw=TOOL_GOMA
      self._lastPoint=None
      self.Msg('goma activada (g)')
    elif keyCode == ord('c'):#Activa modo lápiz
      self._toolDraw=TOOL_CIRCULO
      self.Msg('círculo activado (c)')
    elif keyCode == ord('C'):
      self._toolDraw=TOOL_CUADRADO
      self._lastPoint=None
      self.Msg('Cuadrado activado (C)')
    elif keyCode == ord('S'):
      self._toolDraw=TOOL_SELEC
      self._lastPoint=None
      self.Msg('Selección activa (S)')
    elif keyCode == ord('s'):#aumenta ancho de trazo
      if self._toolDraw!=2:
        if self._penWidth < self.MAX_PEN_WIDTH:
          self._penWidth+=1
          self.Msg('siguiente (s) -- ancho %i'%self._penWidth)
      else:
        if self._eraserWidth<self.MAX_PEN_WIDTH:
          self._eraserWidth+=1
          self.Msg('siguiente (s) -- goma %i'%self._eraserWidth)
    elif keyCode == ord('a'):#disminuye ancho de trazo
      if self._toolDraw!=2:
        if self._penWidth>1:
          self._penWidth-=1
          self.Msg('anterior (a) -- ancho %i'%self._penWidth)
      else:
        if self._eraserWidth>1:
          self._eraserWidth-=1
          self.Msg('anterior (a) -- goma %i'%self._eraserWidth)
    elif keyCode == ord('b'):
      self.drawColour='#ffffff'
      self.Msg('color blanco (b)')
    elif keyCode == ord('n'):
      self.drawColour='#000001'
      self.Msg('color negro (n)')
    elif keyCode == ord('z'):
      self.drawColour='#0000ff'
      self.Msg('color azul (z)')
    elif keyCode == ord('r'):
      self.drawColour='#ff0000'
      self.Msg('color rojo (r)')
    elif keyCode == ord('v'):
      self.drawColour='#00ff00'
      self.Msg('color verde (v)')
    elif keyCode == ord('y'):
      self.drawColour='#ffff00'
      self.Msg('color amarillo (y)')
    elif keyCode == ord('m'):
      self.drawColour='#ff00ff'
      self.Msg('color magenta (m)')
    elif keyCode == ord('x'):
      self.drawColour='#00ffff'
      self.Msg('color cian (x)')
    # Si ha cambiado la herramienta se guarda la figura
    # en la capa de dibujo
    if lastTool != self._toolDraw:
      tool=self._tools[self._toolDraw]
      self.parent.MsgTop('Modo: %s -- %s '%(self.modo,tool))
      self.DropFigure()
      self.DropSelection()

    if lastColour != self.drawColour:
      self.DoPaint()
    
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def Msg(self, s):
    if len( self._sbtxCmd.GetLabel())<55:
      self._sbtxInfo.SetLabel('| Msg: '+s)
    else:
      self._sbtxInfo.SetLabel('')
  def Cmd(self, s=''): 
    self._sbtxCmd.SetLabel(s)
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def OnSize(self,e):
    ancho, alto= self.GetSize()
    w,h= self._bmpDrawCache.GetSize()
    #Actualiza el tamaño de la cache si es más pequeña que el redimensionado
    if ancho>w or alto>h:
      _bmpDrawCache=wx.Bitmap(ancho,alto)
      dc = wx.MemoryDC()
      dc.SelectObject(_bmpDrawCache)
      dc.SetBackground(wx.Brush(self._bgBoardColour))
      dc.Clear()
      #Centra lo que ya existe
      xnew=(ancho-w)//2
      ynew=(alto-h)//2
      dc.DrawBitmap(self._bmpDrawCache, xnew,ynew)
      self._bmpDrawCache=_bmpDrawCache
    
    self.sb.SetSize(ancho,self.sbHeight)
    self.sb.SetPosition((0,alto-self.sbHeight))
    
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def OnLeftClic(self,e):
    pos=e.GetLogicalPosition(wx.BufferedPaintDC(self))
    x,y=pos
    state = wx.GetMouseState()
    if state.ShiftDown() and self._lastPoint !=None:
        # Ajusta para las lineas rectas con la herramienta polígono
        x0,y0= self._lastPoint
        x,y=pos
        dx,dy=abs(x-x0),abs(y-y0)
        if dx>dy:
          pos=wx.Point(x,y0)
        else:
          pos=wx.Point(x0,y)
    self._lastClickLeft=pos
    if self._imodo== MODO_TEXTO:
      self._drawTxt.SetPosition((x,y-10))
    elif self._imodo==MODO_FORMULA:
      self.formula.SetPosition((x,y-10))
      self.DoPaint()
    elif self._imodo==MODO_DIBUJO:#Drawing
      #self._lastPoint=pos
      self._isDraggingFigure=False
      if self._figure !=None:
        self._figure.posIni=self._figure.pos
      if self._selection !=None:
        self._selection.posIni=self._selection.pos
      dc = wx.MemoryDC()
      
      if not self._isDrawing:
        self.SaveLastAction(dc)
      dc.SelectObject(self._bmpDrawCache)
      if self._toolDraw ==TOOL_GOMA:
        dc.SetPen(wx.Pen(self._bgBoardColour,self._eraserWidth, wx.PENSTYLE_CROSS_HATCH ) )
      else:
        dc.SetPen(wx.Pen(self._drawColour,self._penWidth, wx.PENSTYLE_CROSS_HATCH ) )
      
      if self._toolDraw in ( TOOL_GOMA , TOOL_LAPIZ, TOOL_POLIGONO):
        if self._lastPoint == None:
          pos2=(pos.x+1,pos.y)
          dc.DrawLine(pos,pos2)
        else:
          dc.DrawLine(self._lastPoint,pos)
      self.DoPaint()
      print( 'clic en:',self._lastPoint, pos)
      if self._toolDraw == TOOL_LAPIZ:
        self._lastPoint=None
        self._lastPoint2=None
      elif self._toolDraw == TOOL_POLIGONO: #Poligono
        self._lastPoint2 =self._lastPoint
        self._lastPoint=pos
      elif self._toolDraw == TOOL_GOMA: #goma
        self._lastPoint=None
        self._lastPoint2=None
    #self.Msg('pos -- (%i,%i)'%(pos.x,pos.y))
    print('pos -- (%i,%i)'%(pos.x,pos.y))


  def OnRighClic(self,e):
    pos=e.GetLogicalPosition(wx.BufferedPaintDC(self))
    x,y=pos
    if self._imodo== MODO_TEXTO: #texto
      self._drawTxt.SetPosition((x,y-10))
    
    elif self._imodo==MODO_FORMULA: #Formula
      self.formula.SetPosition((x,y-10))
      self.DoPaint()
    
    elif self._imodo==MODO_DIBUJO:#Drawing
      #self._lastPoint=pos
      dc = wx.MemoryDC()
      if not self._isDrawing:
        self.SaveLastAction(dc)
      dc.SelectObject(self._bmpDrawCache)
      if self._toolDraw !=TOOL_GOMA:
        dc.SetPen(wx.Pen(self._bgBoardColour,self._eraserWidth, wx.PENSTYLE_CROSS_HATCH ) )
      else:
        dc.SetPen(wx.Pen(self._drawColour,self._penWidth, wx.PENSTYLE_CROSS_HATCH ) )
      if self._lastPoint == None:
        pos2=(pos.x+1,pos.y)
        dc.DrawLine(pos,pos2)
      else:
        dc.DrawLine(self._lastPoint,pos)
      self.DoPaint()
      #print( 'clic en:',self._lastPoint, pos)
      if self._toolDraw == TOOL_LAPIZ:
        self._lastPoint=None
        self._lastPoint2=None
      elif self._toolDraw == TOOL_POLIGONO: #Poligono
        self._lastPoint2 =self._lastPoint
        self._lastPoint=pos
      elif self._toolDraw == TOOL_GOMA: #Goma
        self._lastPoint=None
        self._lastPoint2=None
    print('pos -- (%i,%i)'%(pos.x,pos.y))


  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DoGetBestSize(self):
    totalWidth, totalHeight= self.GetSize()
    best = wx.Size(totalWidth, totalHeight)
    self.CacheBestSize(best)
    return best



  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DropText(self):
    '''
    Se pasa el texto del _drawTxt a la zona de dibujo
    '''
    x,y=self._drawTxt.GetPosition()
    txt=self._drawTxt.GetLabel()
    font=self._drawTxt.GetFont()
    
    dc = wx.MemoryDC()
    self.SaveLastAction(dc)
    
    dc.SelectObject(self._bmpDrawCache)
    dc.SetFont(font)
    #dc.SetBrush(wx.Brush('#ffffff'))
    dc.SetTextForeground(self._drawColour)
    #dc.DrawBitmap(txtBmp, x, y, useMask=False)
    dc.DrawText(txt,x,y)
    w,h= self._drawTxt.GetSize()
    #dc.DrawRectangle(x,y,w,h)
    print(' DropText in:',x,y, ' w,h:',(w,h))
    self._txbuff=''
    self._drawTxt.SetLabel('')
  
  def DropFormula(self):
    '''
    Se pasa la formula al area de dibujo
    '''
    dc = wx.MemoryDC()
    self.SaveLastAction(dc)
    dc.SelectObject(self._bmpDrawCache)
    x,y=self.formula.GetPosition()
    #self.formula.SetMask(wx.Mask(self.formula, wx.BLACK))
    dc.DrawBitmap(self.formula.bitmap,x,y,1)

  def DropFigure(self,duplicate=False):
    if self._figure == None:
      return
    dc = wx.MemoryDC()
    self.SaveLastAction(dc)
    dc.SelectObject(self._bmpDrawCache)
    normalPen=wx.Pen(self._drawColour, self._penWidth, wx.PENSTYLE_CROSS_HATCH )
    dc.SetBrush(wx.TRANSPARENT_BRUSH)
    dc.SetPen(normalPen)
    self._figure.Draw(dc)
    if not duplicate:
      self._figure=None
      self.Msg('Figura anclada')
    else:
      self.Msg('Figura copiada')
    
  def ClipSelection(self,duplicate=False):
    '''
    Recorta el area seleccionada y la guarda en un bmp aparte
    que se puede mover
    
    '''
    if self._selection == None:
      return
    if self._selectionBmp !=None:
      # intento de cortar una región flotante de selección
      return
    
    self._selectionBmp=self._bmpDrawCache.GetSubBitmap(self._selection.rect)
    self._selectionBmp.SetMaskColour(self._bgBoardColour)
    dc = wx.MemoryDC()
    if not duplicate:
      self.SaveLastAction(dc)
      dc.SelectObject(self._bmpDrawCache)
      # Borra el cuadrado copiado
      dc.SetBrush(wx.Brush(self._bgBoardColour))
      normalPen=wx.Pen(self._bgBoardColour)# ancho 1, solido
      dc.SetPen(normalPen)
      dc.DrawRectangle(self._selection.rect)
      self.Msg('Selección cortada')
    else:
      self.Msg('Selección copiada')
    
  def DropSelection(self,duplicate=False):
    '''
    Suelta la selección sobre el area de dibujo
    '''
    if self._selection == None:
      return
    if self._selectionBmp == None:
      if not duplicate:
        self._selection=None
      return
    dc = wx.MemoryDC()
    self.SaveLastAction(dc)
    dc.SelectObject(self._bmpDrawCache)
    
    x,y=self._selection.pos
    dc.DrawBitmap(self._selectionBmp,x,y,1)
    if not duplicate:
      self._selectionBmp=None
      self._selection=None
      self.Msg('Se ha anclado la selección')
    else:
      self.Msg('Se ha pegado una copia')

  def EraseSelection(self):
    if self._selection == None:
      return
    dc = wx.MemoryDC()
    self.SaveLastAction(dc)
    dc.SelectObject(self._bmpDrawCache)
    # Borra el cuadrado de selección
    dc.SetBrush(wx.Brush(self._bgBoardColour))
    normalPen=wx.Pen(self._bgBoardColour)# ancho 1, solido
    dc.SetPen(normalPen)
    dc.DrawRectangle(self._selection.rect)
    self._selectionBmp=None
    self.DoPaint()

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DoPaint(self):
    '''Realiza el redibujo usual luego de inicializado el control'''
    dc = wx.BufferedPaintDC(self)
    ancho, alto = self.GetSize()
    dc.SetBackground(wx.BLACK_BRUSH)
    
    dc.Clear()

    dc.DrawBitmap(self._bmpDrawCache, 0,0)
    x,y=self.formula.GetPosition()
    if self._imodo == MODO_FORMULA:
      dc.DrawBitmap(self.formula.bitmap,x,y,1) #el uno indica para usar máscara
    if self._selection !=None:
      if self._selectionBmp !=None:
        x,y=self._selection.pos
        dc.DrawBitmap(self._selectionBmp,x,y,1)
      normalPen=wx.Pen(self._drawColour, 1, wx.PENSTYLE_DOT_DASH )
      dc.SetBrush(wx.TRANSPARENT_BRUSH)
      dc.SetPen(normalPen)
      self._selection.Draw(dc)
    if self._imodo == MODO_DIBUJO:
        if self._figure !=None:
          normalPen=wx.Pen(self._drawColour, self._penWidth, wx.PENSTYLE_CROSS_HATCH )
          dc.SetBrush(wx.TRANSPARENT_BRUSH)
          dc.SetPen(normalPen)
          self._figure.Draw(dc)
    #print(' Redibujado')
  
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def Undo(self):
    '''
    Deshace la última modificación del mapa de bits
    '''
    if not self._undoActive:
      return
    dc = wx.MemoryDC()
    # Guarda la última versión para poder deshacer
    tmp=self._bmpDrawUndo
    self._bmpDrawUndo=self._bmpDrawCache
    self._bmpDrawCache=tmp
    if self._slides !=None:
      self._slides._bmpDraw=tmp
    self.DoPaint()
    if self._imodo== MODO_TEXTO:
      #Para redibujar
      x,y = self._drawTxt.GetPosition()
      self._drawTxt.SetPosition((x,y+3))
      self._drawTxt.SetPosition((x,y))
    elif self._imodo== MODO_DIBUJO:
      if self._toolDraw == TOOL_POLIGONO:
        tmp=self._lastPoint2 
        self._lastPoint2=self._lastPoint
        self._lastPoint=tmp
  def SaveLastAction(self, dc):
    '''
    Guarda la última versión del mapa de bits antes de modificarse
    por alguna acción, esto es con el fin de poder 
    deshacer la última acción
    '''
    dc.SelectObject(self._bmpDrawUndo)
    dc.DrawBitmap(self._bmpDrawCache, 0,0)
    self._undoActive=True
    print('  Acción guardada')

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def OnPaint(self, e):
    if self._startedControl:
      self.DoPaint()
    else:
      # Primera vez que se dibuja
      self._startedControl=True
      #self.DrawBitmaps()
      self.DoPaint()
      #print('Se ha dibujado', type(self))

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def OnEraseBackground(self, event):
    """ manipulador del evento  wx.EVT_ERASE_BACKGROUND """
    # Se usa vacío para reducir el flicker
    pass
