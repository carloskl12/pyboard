import wx
import subprocess
from .charequ import CHAR_EQ
from .formulaParser import FormulaParser
class FormulaCtrl(wx.Bitmap):
  '''
  Clase que encapsula un control en el que se dibuja una formula
  matemática. 
  fcolour: color del trazo
  bcolour: color de fondo
  fsize: tamaño de fuente
  mask: indica si el color de fondo se entiende como transparente
  '''
  monoToken='_^+-*/{}()[].,=><'
  def __init__(self,parent, size=(200,50), pos=(0,0), 
    fcolour='#ffffff',bcolour='#000000', fsize=14,fweight=10,mask=True):
    self.pos=pos
    
    super(FormulaCtrl, self).__init__(size[0],size[1])
    self.formula='' #Texto con la fórmula
    self.fcolour=fcolour
    self.bcolour=bcolour
    self.fsize=fsize
    self.fweight=fweight
    self.font = wx.Font( wx.FontInfo(fsize).Family(wx.FONTFAMILY_SWISS) )
    self.mask=mask
    self.strings=['']
    self.operators=['s']#nodo actual
    self.envlvl=[0]#Nivel del nodo actual
    self.factor=0.7 #Factor en cada subida de nivel
    
    self.parser=FormulaParser('')
    self.DrawBitMap('')
    #self.holdstring=False
    
  def SetPosition(self, pos):
    self.pos=pos
  
  def GetPosition(self):
    return self.pos
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def __call__(self, formula=None):
    '''
    Actualiza la fórmula
    '''
    if formula!=None:
      self.formula=formula
      self.Update()
      print(' formula:',formula)
    return self.bitmap
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def Update(self):
    render=True
    clearBmp=True
    if self.formula=='' or self.formula==' ':
      render=False
    try:
      if render:
        self.parser(self.formula)
        self.parser.treeRoot.DepureTree()
    except Exception as e:
      print('  ** Error parseando')
      print(e)
      render=False
      clearBmp=False
      return
    
    dc = wx.MemoryDC()
    dc.SelectObject(self)
    dc = wx.GCDC(dc)
    ancho, alto = self.GetSize()
    dc.SetBackground(wx.Brush(self.bcolour))
    if clearBmp:
      dc.Clear()
    dc.SetTextForeground(self.fcolour)
    
    try:
      if render:
        pass
        self.parser.treeRoot.FindSize(dc,self.fsize)
      #print('  * treeRoot:Dimensiones halladas')
    except Exception as e:
      print('error mientras halla tamaño')
      print(e)
      rende=False
    
    try:
      if render:
        pass
        self.parser.treeRoot.DrawBox(dc,self.fcolour)
      #print('  * treeRoot:formula dibujada')
    except Exception as e:
      print('error mientras dibuja')
      print(e)
      render=False
    
    
    width,height=5,5
    if render:
      width, height = self.parser.treeRoot.width,self.parser.treeRoot.height
      if width==0 or height ==0:
        width,height=5,5
        
    self.textSize=(width,height)
    #print('  * textSize:',self.textSize)
    dc.SetBrush(wx.TRANSPARENT_BRUSH)
    #dc.DrawRectangle(0,0,x,maxy)
    
    self.bitmap=self.GetSubBitmap(wx.Rect(0,0,width,height))
    #self.bitmap.SetMask(wx.Mask(self.bitmap,self.bcolour))
    self.bitmap.SetMaskColour(self.bcolour)
    #print('  *** bcolour',self.bcolour)
    return self.bitmap

  def Updatex(self):
    #Indice usado por la lectura de tokens sobre el string de formula 
    
    sbuff=''
    #Arbol que almacena un formato facil de interpretar para visualizar
    self.strings=['']
    self.operators=['s']#nodo actual
    self.it=0 
    t=self.Token()
    render=True #Para indicar si se renderiza o no
    self.envlvl=[0]
    if t == None:
      self.DrawBitMap('')
    while t != None:
      sbuff+=t
      try:
        self.BuildTree(t)
      except Exception as e:
        print(e)
        render=False
      #print('  token:',t)
      try:
        t=self.Token()
        if t=='\\ ':
          print('  xx 777 espacio por fin')
      except  Exception as e:
        print(e)
        render=False
        break
    if render:
      self.DrawBitMap(sbuff)
      return 1
    return 0
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def Token(self):
    '''
    Generador de tokens
    '''
    if self.it< len(self.formula):
      c=self.formula[self.it]
      ic=ord(c)
      self.it+=1
      if 64<ic<91 or 96<ic<123 or 47< ic<58:
        return c
      if c in  self.monoToken:
        return c
      elif c == '\\':
        #Comandos o carácteres de escape
        if self.it < len(self.formula):
          cc=self.formula[self.it]
          ic=ord(cc)
          if ic== 32:
            self.it+=1
            return '\\ '
          while 64<ic<91 or 96<ic<123:#alfabético
            c+=cc
            self.it+=1
            if self.it < len(self.formula):
              cc=self.formula[self.it]
              ic=ord(cc)
            else:
              break
          return c
      elif c == ' ':
        return ' '
      else:
        return c
    return None
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DrawBitMap(self,stex):
    '''
    Procesa un string, y t es el último token
    '''
#    print( '  strings:', self.strings)
#    print( '  lvls:', self.envlvl)
#    print( '  cms:',self.operators)

    dc = wx.MemoryDC()
    dc.SelectObject(self)
    ancho, alto = self.GetSize()
    dc.SetBackground(wx.Brush(self.bcolour))
    dc.Clear()
    
    dc.SetTextForeground(self.fcolour)
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Calcula las alturas de las lineas base según los niveles
    # para superíndices y subíndices
    # primero obtiene las métricas de las fuentes
    fsize=self.fsize
    metrics=[]
    ltFonts=[]
    for lvl in range(max(self.envlvl)+1):
      fsize=round(self.fsize*self.factor**lvl)
      font = wx.Font( wx.FontInfo(fsize).Family(wx.FONTFAMILY_SWISS) )
      dc.SetFont(font)
      ltFonts.append(font)
      # ascent altura sobre la linea base
      # descent altura bajo la linea base
      # height altura total
      # averageWidth altura de una x
      fmetrics= dc.GetFontMetrics()
      v=[fmetrics.ascent, fmetrics.descent, fmetrics.height, fmetrics.averageWidth]
      #print(' metrics:',v)
      metrics.append(v)
    # linea base de superíndices
    ybaseUp=[]#Alturas según los niveles
    ydeltaUp=[]#Variaciones entre niveles
    ap,dp,hp,vp=0,0,0,0
    for a, d, h, v in metrics[::-1]:
      if ap==0:
        ybaseUp.append(0)
        ydeltaUp.append(0)
      else:
        dy=ap-a+v
        lasty=ybaseUp[-1]
        ybaseUp.append(lasty+dy)
        ydeltaUp.append(dy)
      ap,dp,hp,vp=a,d,h,v
    
    ybaseUp=ybaseUp[::-1]
    ydeltaUp=ydeltaUp[::-1]
    ydeltaUp=[0]+ydeltaUp[:-1]
    # linea base subíndices
    ybaseDown=[]
    ydeltaDown=[]
    ap,dp,hp,vp=0,0,0,0
    for a, d, h, v in metrics:
      if ap==0:
        ybaseDown.append(ybaseUp[0])
        ydeltaDown.append(0)
      else:
        dy=ap -a +v
        lasty=ybaseDown[-1]
        ybaseDown.append(lasty+dy)
        ydeltaDown.append(dy)
      ap,dp,hp,vp=a,d,h,v
    
#    print('  ybaseUp:',ybaseUp)
#    print('  ybaseDown:',ybaseDown)
#    print('  ydeltaUp:',ydeltaUp)
#    print('  ydeltaDown',ydeltaDown)
    # Calcula las posiciones de cada texto
    # superíndices y subíndices
    miny=200
    maxy=0
    plvl=0
    y=ybaseDown[0]
    lasInc=[]
    ytext=[]
    for lvl, op in zip(self.envlvl, self.operators):
      if op == '^':
        if plvl < lvl:
          lasInc.append(ydeltaUp[lvl])
          y-=lasInc[-1]
        elif plvl> lvl:
          y+=lasInc.pop()
      elif op == '_':
        if plvl < lvl:
          lasInc.append(ydeltaDown[lvl])
          y+=lasInc[-1]
        elif plvl> lvl:
          y-=lasInc.pop()
      if lvl == 0:
        y=ybaseUp[0]
      #print('  y:',y ,'  lasInc:',lasInc)
      ytext.append(y)
      if y < miny:
        miny=y
      # la altura total 
      ytotal=y+metrics[lvl][2]
      if ytotal> maxy:
        maxy=ytotal
      plvl=lvl
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #Dibuja los textos
    if miny != 0:
      ytext=[y-miny for y in ytext]
      maxy-=miny
      #miny=0
#    print( '  *y:',ytext)
#    print('  *ymax:',maxy)
#    print('  hfonts:',[ v[2] for v in metrics])
    x=0
    y=ybaseDown[0]
    plvl=0
    lasInc=[]#Ultimo incremento para deshacer cuando disminuye
    for lvl, op , s ,yt in zip(self.envlvl, self.operators,self.strings, ytext):
      dc.SetFont(ltFonts[lvl])
      wtext,htext=dc.GetTextExtent(s)
      dc.DrawText(s,x,yt)
      x+=wtext+fsize//8
      plvl=lvl
    self.textSize=(x,maxy)
    #print('  * textSize:',self.textSize)
    dc.SetBrush(wx.TRANSPARENT_BRUSH)
    #dc.DrawRectangle(0,0,x,maxy)
    
    self.bitmap=self.GetSubBitmap(wx.Rect(0,0,x,maxy))
    self.bitmap.SetMask(wx.Mask(self.bitmap,self.bcolour))
    return self.bitmap
    

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def BuildTree(self,t):
    '''
    Construye el arbol de vista usando operators, y strings 
    '''
    # cambia los comandos de escape de glifos únicos
    
    if t == ' ':
      print('\n** Token espacio')
      if self.envlvl[-1] > 0:
        lvl=self.envlvl[-1]
        #Si el operador anterior son de los que cambian
        # el tamaño de la fuente se reduce un nivel
        operator='s'
        if self.operators[-1] in ('_','^'):
          lvl-=1
          if lvl > 0:
            operator=self.DownLvlOperator()
          
        self.envlvl.append(lvl)
        self.operators.append(operator)
        self.strings.append('')
    else:
      if len(t) > 1:
        tchar=t[1:]
        if tchar in CHAR_EQ:
          t=CHAR_EQ[tchar]
      # incremento de profundidad  (reducción del tamaño de fuente)
      #print('  *** Espacio',t,len(t))
      if t in ('_','^'):#, '\\f','\\s'):
        self.operators.append(t)
        self.strings.append('')
        if self.operators[-1] == t or self.operators[-1]=='s':
          self.envlvl.append(self.envlvl[-1]+1)
        elif self.operators[-1] in ('_','^'):
          self.envlvl.append(self.envlvl[-1])
        else:
          raise Exception('Invalid format')
      elif len(t)== 1:
        self.strings[-1]+=t
      

  def DownLvlOperator(self):
    '''
    Obtiene el operador de nivel inferior al 
    actual
    '''
    n= len(self.operators)
    op='s'
    if n > 1:
      op=self.operators[-1]
    return op



