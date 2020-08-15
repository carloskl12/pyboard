'''
Diferentes clases para parsear y graficar las fórmulas

revisar parserFórmula.ods
'''
import wx


class Box(object):
  '''
  Clase padre de las diferentes unidades para graficar
  
  root es el nodo raíz
  '''
  def __init__(self,root, parent=None,content=None,fontSizeLvl=None,fontNormalSize=14):
    self.root=root
    self.parent=parent
    self.fontNormalSize=fontNormalSize
    #Pos x,y donde ubicarse
    self.x=0 
    self.y=0
    #Ancho y alto que ocupará esta unidad
    self.width=0
    self.height=0
    self.drawable=False #Si está listo para dibujarse
    self.stage=0 #Etapas en la lectura de esta unidad
    #Contenido de la caja
    self.d=[]
    if content != None:
      if isinstance(content, list):
        self.d= content
      elif isinstance(content,tuple):
        #Es una tupla valor, tt
        # usada para un token, y tipo de token
        self.append(*content)
      else:
        self.append(content)
    # Nivel de la fuente que define su tamaño
    self.fontSizeLvl=fontSizeLvl
    if fontSizeLvl == None and parent !=None:
      # Hereda del padre el nivel de la fuente a utilizar
      self.fontSizeLvl=parent.fontSizeLvl
    if self.fontSizeLvl == None:
      self.fontSizeLvl=1

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  @property
  def fullParse(self):
    # Si la etapa es -1 indica que se terminó esta unidad
    return self.stage==-1

  @property
  def gx(self):
    #coordenaga global de x
    return self.x+self.parent.gx
  @property
  def gy(self):
    #coordenaga global de x
    return self.y+self.parent.gy
  @property
  def gPos(self):
    return (self.gx, self.gy)

  @property
  def pos(self):
    return (self.x,self.y)
  @property
  def size(self):
    return (self.width,self.height)
  @size.setter
  def size(self, sz):
    self.width,self.height=sz

  @property
  def currentBox(self):
    return self.root.currentBox
    

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def SetPos(self,x,y):
    self.x=x
    self.y=y

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def append(self, value, tt):
    '''
    Este método se debe sobreescribir para indicar las reglas particulares
    de cada unidad de expresión 
    '''
    raise Exception('  Patrón de procesamiento no implementado')
#    self.d.append(value)
#    self.stage+=1
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def endAppend(self, value=None, tt=None):
    '''
    Finaliza el nodo hijo que se estaba leyendo
    
    value y tt se pueden utilizar para procesar tokens que no se 
    procesaron en el nodo hijo, es decir, simplemente desencadenó 
    su finalización
    '''
    unidad= self.d[-1]
    if isinstance(unidad,Box):
      if not unidad.fullParse:
        raise Exception('  No se finalizó correctamente el nodo hijo')
    self.root.currentBox= self
    if value!=None and tt !=None:
      self.append(value,tt)
  
  def __getitem__(self, index):
    return self.d[index]
  
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def __str__(self):
    if not hasattr(self,'_lvlIndent'):
      self._setIndent(0)
    indent='  '*(self._lvlIndent)
    indent2='  '*(self._lvlIndent+1)
    s='\n%s%s:['%(indent,type(self).__name__)
    for v in self.d:
      if isinstance(v,Box):
        v._setIndent(self._lvlIndent+1)
      ss=str(v)
      if ss[0]=='\n' and s[-1]=='\n':
        #Para evitar el doble salto de linea
        ss=ss[1:]
      if ss[-1]=='\n':
        s+=ss
      else:
        s+=ss+' ' 
      
    if s[-1]=='\n':
      s+='%s]\n'%indent
    else:
      s+=']\n'
    return s
  def _setIndent(self,value):
    '''
    Se utiliza para indentar el arbol al mostrarse como string
    '''
    self._lvlIndent=value
    
  def _printBoxMetrics(self,head=False, name=None):
    '''
    Imprime las métricas de la caja, se utilza para 
    debugg
    '''
    if head:
      print( '  name \t\tascent \tdescent\txwidth\tha\th')
    if name==None:
      name=type(self).__name__
    print('  %s\t%i\t%i\t%i\t%i\t%i'%(str(name),self._ascent,self._descent, 
        self._averageWidth, self._ascent-self._averageWidth, self.height))
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def FindSize(self, dc, fontNormalSize=None):
    '''
    Calcula el ancho y alto de la caja en casos secuenciales como 
    RootBox, y GroupBox
    '''
    if  self.currentBox != None:
      '''
      termina el símbolo de integra para que se pueda 
      visualizar bien mientras se está escribiendo
      '''
      if isinstance(self.currentBox, IntBox):
        self.currentBox.DepureTree()
        if self.currentBox.parent.d==[]:
          self.currentBox.parent.d.append(self.currentBox)
        elif self.currentBox.parent.d[-1] != self.currentBox:
          self.currentBox.parent.d.append(self.currentBox)

    if len(self.d)==0:
      return
    if fontNormalSize !=None:
      self.fontNormalSize=fontNormalSize
    self._ascent=0 #Altura sobre la linea base
    self._descent=0 #altura bajo la linea base
    self._averageWidth=0 #altura de una x
    self._fsize=0 #tamaño de fuente
    self.width=0
    box=None
    
    
    for box in self.d:
      box.fontSizeLvl=self.fontSizeLvl
      box.fontNormalSize=self.fontNormalSize
      box.x=self.width
      print( '  box:',type(self).__name__,'  box.x',box.x)
      box.FindSize(dc)
      print('  **dimHallada')
      if self._ascent < box._ascent:
        self._ascent=box._ascent
      if self._descent < box._descent:
        self._descent=box._descent
      self.width+=box.width
      
    self.height=self._ascent+self._descent
    font, fsize= self.GetFont()
    self._fsize=fsize
    dc.SetFont(font)
    fmetrics= dc.GetFontMetrics()
    #self._fmetrics=fmetrics
    self._averageWidth=fmetrics.averageWidth
    self._internalLeading=fmetrics.internalLeading # espacio extra superior
    self._externalLeading=fmetrics.externalLeading # espacio entre lineas
    #%%%%%%%%%%%%%%%%%%%%%%%%%%
    # posiciona los boxes en y, para que las linea base coincidan
    for box in self.d:
      if box._ascent != self._ascent:
        box.y= self._ascent - box._ascent
    
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def GetFont(self, fontSizeLvl=None,fontNormalSize=None,family=wx.FONTFAMILY_SWISS):
    '''
    Calcula la fuente según un nivel de profundidad, si el valor es 0, indica 
    que es el tamaño base, si es postivo, se va disminuyendo su tamaño,
    en cambio si es negativo se hace más grande que el tamaño normal
    '''
    if fontSizeLvl == None:
      fontSizeLvl=self.fontSizeLvl
    if fontNormalSize == None:
      fontNormalSize=self.fontNormalSize
    factor=0.74 #Define como varía el tamaño de la fuente
    fsize=round(fontNormalSize*factor**fontSizeLvl)
    font = wx.Font( wx.FontInfo(fsize).Family(wx.FONTFAMILY_SWISS) )
    return (font , fsize)
  
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DrawBox(self, dc):
    '''
    Dibuja la caja, dibujando cada uno de sus elementos
    '''
    for box in self.d:
      box.DrawBox(dc)
  
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DepureTree(self):
    if len(self.d)>1:
      for box in self.d[:-1]:
        if not box.fullParse:
          raise Exception('  Error en la unidade %s'%type(box).__name__)
    #Solo se depura la última unidad
    box=self.d[-1]
    if not box.fullParse:
      if len(box.d)== 0:
        #Se elimina el último valor si no hay nada
        self.d.pop()
      else:
        box.DepureTree()
      self.stage=-1
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class RootBox(Box):
  '''
  Clase que encapsula el nodo raíz en el arbol sintáctico
  '''
  def __init__(self, **kwargs):
    super(RootBox,self).__init__(self,None,**kwargs)
    self._currentBox=self

  @property
  def gx(self):
    #coordenaga global de x
    return self.x
  
  @property
  def gy(self):
    #coordenaga global de x
    return self.y

  @property
  def currentBox(self):
    return self._currentBox
    
  @currentBox.setter
  def currentBox(self, value):
    self._currentBox=value
  
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def append(self, value, tt=None):
    '''
    todo valor que acepta el root debe ser un token 
    '''
    if not isinstance(value, str):
      raise Exception('  root: error, solo se aceptan strings para concatenar')
    box=None
    if tt == '{':
      #Crea un grupo y lo agrega a los datos de forma interna
      box=GroupBox(self.currentBox,self)
    elif value in PREFIJOS:
      box= PREFIJOS[value](self.currentBox,self)
    elif value in INFIJOS:
      if len(self.d)==0:
        raise Exception('  root: los operadores infijos requieren una unidad previa')
      unidad = self.d.pop()
      print(  'unidad:', unidad)
      box =INFIJOS[value](self.currentBox,self,content=(unidad,None))
    elif tt == 'c':
      box= StringBox(self.currentBox,self, content=(value,tt))
    else:
      raise Exception('  %s: el token "%s" no es válido'%(type(self).__name__, value))
    #Si se crea un box, este se agrega y pasa a ser el nodo actual
    if box != None:
      self.d.append(box)
      self.currentBox=box

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DrawBox(self, dc,fcolour):
    '''
    Dibuja la caja, dibujando cada uno de sus elementos
    fcolour es necesario para dibujar la raíz cuadrada
    '''
    self.fcolour=fcolour
    for box in self.d:
      box.DrawBox(dc)
  
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class GroupBox(Box):
  '''
  Clase que encapsula el nodo raíz en el arbol sintáctico
  '''
  def __init__(self,root, parent, **kwargs):
    super(GroupBox,self).__init__(root,parent,**kwargs)

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def append(self, value, tt):
    '''
    todo valor que acepta el group debe ser un token 
    '''
    if not isinstance(value, str):
      raise Exception('  group: error, solo se aceptan strings para concatenar')
    box=None
    if tt == '{':
      #Crea un grupo y lo agrega a los datos de forma interna
      box=GroupBox(self.root,self)
    elif tt == '}':
      self.stage=-1 #finaliza nodo
      self.parent.endAppend() #Sube un nivel
    elif value in PREFIJOS:
      box= PREFIJOS[value](self.root,self)
    elif value in INFIJOS:
      if len(self.d)==0:
        raise Exception('  group: los operadores infijos requieren una unidad previa')
      unidad = self.d.pop()
#      if isinstance(unidad,StringBox):
#        if len(unidad.d) == 2:
#          # noc c c opinfijo  
#          self.d.append(unidad.d[0])
#          unidad= unidad.d[1] #solo toma el caracter
      box =INFIJOS[value](self.root,self,content=unidad)
    elif tt == 'c':
#      unidad=None
#      if len(self.d)>0:
#        unidad= self.d[-1]
#      if not isinstance(unidad,str):
#        # La unidad anterior no debe ser un caracter
#        self.d.append(value)
#      else:
#        # la unidad anterior es un caracter
#        self.d.pop()#Elimina el último caracter agregado (unidad)
#        box= StringBox(self.root,self, content=[unidad, value])
      box= StringBox(self.root,self, content=(value,tt))
    else:
      raise Exception('  %s: el token "%s" no es válido'%(type(self).__name__, value))
    
    #Si se crea un box, este se agrega y pasa a ser el nodo actual
    if box != None:
      self.d.append(box)
      self.root.currentBox=box

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class SqrtBox(Box):
  '''
  Clase que encapsula el nodo raíz en el arbol sintáctico
  '''
  def __init__(self,root, parent, **kwargs):
    super(SqrtBox,self).__init__(root,parent,**kwargs)

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def append(self, value, tt=None):
    '''
    value puede ser un toke o un box
    tt indica el tipo de token
    '''
    vr=None #Valor a retornar, si se consume no retorna nada
    if not isinstance( value,str):
      raise Exception('  %s: el valor a agregar no es una unidad válida'%(type(self).__name__))
    if self.stage ==0:
      # primer parámetro a agregar
      if value == '[':
        if len(self.d)>0:
          raise Exception('  %s: sintaxis inválida para argumentos'%(type(self).__name__))
        box=ArgBox(self.root,self)
        self.d.append(box)
        self.root.currentBox=box
        self.stage=10 # Sirve para el endAppend
        
        fontx, fsizex= self.d[0].GetFont()
        print('  sqrt creación h argbox:',box.fontSizeLvl)
        print('  sqrt creación h argbox:',box.fontNormalSize)
      elif tt == 'c':
      #if isinstance(value, str):
        value= StringBox(self.root,self,content=(value,tt))
        value.stage=-1
        self.d.append(value)
        self.stage=-1
        self.parent.endAppend()
      elif tt=='{':
        box=GroupBox(self.root,self)
        self.d.append(box)
        self.root.currentBox=box
        self.stage=11 # Sirve para el endAppend
      else:
        raise Exception('  %s: sintaxis inválida'%(type(self).__name__))
    else:
      raise Exception('  %s: en el estado %i no se aceptan valores'%( type(self).__name__,self.stage) )
  
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def  endAppend(self, value=None, tt=None):
    # solo puede finalizar una vez la entrada del exponente
    # con lo cula finaliza la lectura de la potencia
    super(SqrtBox,self).endAppend(value,tt)
    if self.stage == 10:
      self.stage=0
    elif self.stage == 11:
      self.stage=-1
      self.parent.endAppend()
    else:
      raise Exception('  %s: sintaxis inválida al finalizar un grupo'%(type(self).__name__))

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def FindSize(self, dc):
    '''
    Calcula el ancho y alto de la caja
    '''
    font, fsize= self.GetFont()
    dc.SetFont(font)
    self._fsize=fsize
    self._interlineado=round(self._fsize/4)
    fmetrics= dc.GetFontMetrics()
    #v=[fmetrics.ascent, fmetrics.descent, fmetrics.height, fmetrics.averageWidth]
    box=self.d[0]
    if len(self.d)==2:
      self.d[0].fontSizeLvl=self.fontSizeLvl+2
      self.d[0].fontNormalSize=self.fontNormalSize
      box=self.d[1]
      
    box.fontSizeLvl=self.fontSizeLvl
    box.fontNormalSize=self.fontNormalSize
    box.x=fmetrics.averageWidth+self._interlineado
    
    box.FindSize(dc)
    if box.height/fmetrics.height > 2:
      box.x+=self._interlineado
      #print('  *****se ejecuto:', box.x)
    #Separación del siguiente box
    self.width=box.x+box.width+self._interlineado
    self.height=box.height
    box._printBoxMetrics(head=True)
    hx=fmetrics.averageWidth
    h=box.height
    p1y=box._ascent-round(hx/2)
    p1x=0
    p2y=h
    p2x=round(hx/2)
    p3y=0
    p3x=hx
    p4y=p3y
    p4x=self.width-self._interlineado
    #Calcula el trazo para la raiz
    self._points=[(p1x,p1y),(p2x,p2y),(p3x,p3y),(p4x,p4y)]
    
    self._ascent=box._ascent #Altura sobre la linea base
    self._descent=box._descent #altura bajo la linea base
    self._averageWidth=box._averageWidth #altura de una x
    
    self._internalLeading=fmetrics.internalLeading # espacio extra superior
    self._externalLeading=fmetrics.externalLeading # espacio entre lineas

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DrawBox(self, dc):
    '''
    Dibuja la caja, dibujando cada uno de sus elementos
    '''
    #Dibuja la raíz
    lineWidth=round(self._fsize/8)
    pen=wx.Pen(self.root.fcolour, lineWidth, wx.PENSTYLE_CROSS_HATCH )
    dc.SetPen(pen)
    gx,gy=self.gPos
    for i in range(len(self._points)-1):
      px1,py1=self._points[i]
      px2,py2=self._points[i+1]
      p1=px1+gx,py1+gy
      p2=px2+gx,py2+gy
      dc.DrawLine(p1,p2)
    box=self.d[0]
    if len(self.d)==2:
      indice=self.d[0]
      indice.DrawBox(dc)
      box=self.d[1]
    box.DrawBox(dc)
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DepureTree(self):
    '''
    Se utiliza para depurar una entrada sin terminar, con el fin de que se pueda
    mostrar
    '''
    if not self.fullParse:
      if len(self.d)== 1:
        if not self.d[0].fullParse:
          self.d[0].DepureTree()
        if self.stage == 10 or isinstance(self.d[0],ArgBox):
          #En espera de finalizar el argumento
          # y sin radicando
          box=StringBox(self.root,self,content=(' ','c'))
          box.stage=-1
          self.d.append(box)
        
      elif len(self.d)== 2:
        self.d[1].DepureTree()
      self.stage=-1

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class IntBox(Box):
  '''
  Clase para encapsular el símbolo de integral
  '''
  def __init__(self,root, parent, **kwargs):
    super(IntBox,self).__init__(root,parent,**kwargs)
    print(self.parent)
    #self.parent.endAppend()
  
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def FindSize(self, dc):
    '''
    Calcula el ancho y alto de la caja
    '''
    s='∫'
    fontSizeLvl=self.fontSizeLvl-2 #para que sea más grande
    font, fsize= self.GetFont(fontSizeLvl)
    dc.SetFont(font)
    fmetrics= dc.GetFontMetrics()
    #v=[fmetrics.ascent, fmetrics.descent, fmetrics.height, fmetrics.averageWidth]
    wtext,htext=dc.GetTextExtent(s)
    #Separación del siguiente box
    self.width=wtext+round(fsize//8)
    self.height=htext
    self._ascent=fmetrics.ascent #Altura sobre la linea base
    self._descent=fmetrics.descent #altura bajo la linea base
    self._averageWidth=fmetrics.averageWidth #altura de una x
    self._fsize=fsize
    self._internalLeading=fmetrics.internalLeading # espacio extra superior
    self._externalLeading=fmetrics.externalLeading # espacio entre lineas
    print(' int x,y', self.x,self.y)
  
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def append(self,value,tt):
    '''
    Finaliza con cualquier valor que se agregue
    '''
    self.stage=-1 #finaliza lectura del string
    self.parent.endAppend(value, tt)

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DrawBox(self, dc):
    '''
    Dibuja la caja
    '''
    s='∫'
    fontSizeLvl=self.fontSizeLvl-2 #para que sea más grande
    font, fsize= self.GetFont(fontSizeLvl)
    dc.SetFont(font)
    dc.DrawText(s,self.gx, self.gy)
    #print('  string dibjado:',s)
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DepureTree(self):
    self.stage=-1 #finaliza
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class ArgBox(Box):
  '''
  Clase que encapsula el nodo para el argumento extra de un comando
  '''
  def __init__(self,root, parent, **kwargs):
    super(ArgBox,self).__init__(root,parent,**kwargs)

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def append(self, value, tt):
    '''
    value debe ser un token, tt indica es su tipo 
    '''
    if not isinstance( value,str):
      raise Exception('  %s: el valor a agregar no es una unidad válida'%(type(self).__name__))
    if self.stage ==0:
      if value==']':
        raise Exception('  %s: síntaxis inválida, no hay argumento'%(type(self).__name__))
      elif tt == 'c':
        self.d.append(value)
        self.stage=1
      else:
        raise Exception('  %s: sintaxis inválida'%(type(self).__name__))
    elif self.stage== 1:
      #Ya existe al menos un elemento como argumento
      if value==']':
        self.stage=-1
        self.parent.endAppend()
      elif tt == 'c':
        self.d.append(value)
        self.stage=1
      else:
        raise Exception('  %s: sintaxis inválida'%(type(self).__name__))
  
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def FindSize(self, dc):
    '''
    Calcula el ancho y alto de la caja
    '''
    s=''.join(self.d) #Obtiene el string
    font, fsize= self.GetFont()
    dc.SetFont(font)
    fmetrics= dc.GetFontMetrics()
    #v=[fmetrics.ascent, fmetrics.descent, fmetrics.height, fmetrics.averageWidth]
    wtext,htext=dc.GetTextExtent(s)
    #Separación del siguiente box
    self.width=wtext+round(fsize//8)
    self.height=htext
    self._ascent=fmetrics.ascent #Altura sobre la linea base
    self._descent=fmetrics.descent #altura bajo la linea base
    self._averageWidth=fmetrics.averageWidth #altura de una x
    self._fsize=fsize
    self._internalLeading=fmetrics.internalLeading # espacio extra superior
    self._externalLeading=fmetrics.externalLeading # espacio entre lineas
    
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DrawBox(self, dc):
    '''
    Dibuja la caja
    '''
    s=''.join(self.d) #Obtiene el string
    font, fsize= self.GetFont()
    print('  ***2 fsize argbox:',fsize)
    dc.SetFont(font)
    dc.DrawText(s,self.gx, self.gy)
  
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DepureTree(self):
    if len(self.d)==0:
      self.d.append(' ')
    self.stage=-1 #finaliza
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class FracBox(Box):
  '''
  Clase que encapsula el nodo raíz en el arbol sintáctico
  '''
  def __init__(self,root, parent, **kwargs):
    super(FracBox,self).__init__(root,parent,**kwargs)

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def append(self, value, tt=None):
    '''
    value puede ser un toke o un box
    tt indica el tipo de token
    '''
    vr=None #Valor a retornar, si se consume no retorna nada
    if not isinstance( value,str):
      raise Exception('  %s: el valor a agregar no es una unidad válida'%(type(self).__name__))
    if self.stage ==0:
      # primer parámetro a agregar
      if tt == 'c':
        value= StringBox(self.root,self,content=(value,tt))
        value.stage=-1
        self.d.append(value)
        self.stage=1
      elif tt=='{':
        box=GroupBox(self.root,self)
        self.d.append(box)
        self.root.currentBox=box
        self.stage=2 # Sirve para el endAppend
      else:
        raise Exception('  %s: sintaxis inválida para el numerador'%(type(self).__name__))
    elif self.stage == 1:
      # Espera el segundo parámetro
      if tt=='c':
        value= StringBox(self.root,self,content=(value,tt))
        value.stage=-1
        self.d.append(value)
        self.stage=-1
        self.parent.endAppend()
      else:
        raise Exception('  %s: sintaxis inválida para el denominador'%(type(self).__name__))
    elif self.stage == 3:
      #Recibe el segundo grupo
      if tt=='{':
        box=GroupBox(self.root,self)
        self.d.append(box)
        self.root.currentBox=box
        self.stage=4
      else:
        raise Exception('  %s: sintaxis inválida para el denominador'%(type(self).__name__))
    else:
      raise Exception('  %s: en el estado %i no se aceptan valores'%( type(self).__name__,self.stage) )
  
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def  endAppend(self, value=None, tt=None):
    # solo puede finalizar una vez la entrada del exponente
    # con lo cual finaliza la lectura de la potencia
    super(FracBox,self).endAppend(value,tt)
    if self.stage == 4:
      self.stage=-1
      self.parent.endAppend()
    elif self.stage == 2:
      self.stage=3
    else:
      raise Exception('  %s: sintaxis inválida al finalizar un grupo'%(type(self).__name__))

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def FindSize(self, dc):
    '''
    Calcula el ancho y alto de las subcajas, su 
    posicionamiento vertical se da en cada caso particular
    '''
    self.width=0
    # base de la potencia
    self.d[0].fontSizeLvl=self.fontSizeLvl
    self.d[0].fontNormalSize=self.fontNormalSize
    self.d[0].FindSize(dc)
    self.width+=self.d[0].width
    
    self._internalLeading=self.d[0]._internalLeading # espacio extra superior
    self._externalLeading=self.d[0]._externalLeading # espacio entre lineas
    self._averageWidth=self.d[0]._averageWidth
    self._ascent=self.d[0]._ascent
    self._descent=self.d[0]._descent
    self._fsize=self.d[0]._fsize
    
    self._interlineado=round(self._fsize/4)
    
    #self.d[1].x=self.width
    self.d[1].fontSizeLvl=self.fontSizeLvl 
    self.d[1].fontNormalSize=self.fontNormalSize
    self.d[1].FindSize(dc)
    self.width+=self.d[1].width
    
    # Posiciona la raya de la fracción
    font, fsize= self.GetFont()
    dc.SetFont(font)
    w=self.d[0].width
    if self.d[1].width > w:
      w=self.d[1].width
    # Calcula la longitud aproximada de una raya
    s='_'*12
    wtext,htext=dc.GetTextExtent(s)
    wraya= wtext/12
    nrayas=round(w/wraya)+1
    # Define el string de raya y donde se dibujará
    self._barra='_'*nrayas
    fmetrics= dc.GetFontMetrics()
    self._xbarra= 0
    self._ybarra= self.d[0]._ascent - fmetrics.ascent+ round(1.5*self._interlineado)
    wtext,htext=dc.GetTextExtent(self._barra)
    #Calcula el ancho de la caja mas un externalLeading a lado y lado
    
    self.width=wtext+2*self._interlineado
    print('  interlineado',self._interlineado)
    #posiciona numerador
    self.d[0].x= round((wtext-self.d[0].width)/2)
    
    #posiciona el denominador
    self.d[1].x= round((wtext-self.d[1].width)/2)
    self.d[1].y= self.d[0].height+2*self._interlineado
    
    #dimensiones de la caja
    self._ascent=self.d[0].height+3*self._interlineado
    self._descent=self.d[1].height-1*self._interlineado
    self.height=self._ascent+self._descent

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DrawBox(self, dc):
    '''
    Dibuja la caja
    '''
    self.d[0].DrawBox(dc)
    self.d[1].DrawBox(dc)
    font, fsize= self.GetFont()
    dc.SetFont(font)
    dc.DrawText(self._barra,self.gx+self._xbarra, self.gy+self._ybarra)

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DepureTree(self):
    '''
    Se utiliza para depurar una entrada sin terminar, con el fin de que se pueda
    mostrar
    '''
    if not self.fullParse:
      if len(self.d)== 1:
        if not self.d[0].fullParse:
          self.d[0].DepureTree()
        box=StringBox(self.root,self,content=(' ','c'))
        box.stage=-1
        self.d.append(box)
      elif len(self.d)== 2:
        self.d[1].DepureTree()
      self.stage=-1

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class StringBox(Box):
  '''
  Encapsula un string normal
  '''
  def __init__(self, root,parent, content=None):
    super(StringBox,self).__init__(root, parent, content=content)

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def append(self, value, tt):
    '''
    value debe ser un token 
    tt indica el tipo de token
    '''
    vr=None #Valor a retornar, si se consume no retorna nada
    if not self.fullParse:
      if isinstance(value,str):
        if  tt=='c':
          self.d.append(value)
        elif tt in ('}','{') :
          vr=value
        elif value in INFIJOS or value in PREFIJOS:
          vr=value
        else:
          raise Exception('  Formato no válido para continuar "%s"'%tt)
      else:
        raise Exception('  Patrón no válido para continuar "%s"'%tt)
    if vr != None:
      self.stage=-1 #finaliza lectura del string
      self.parent.endAppend(vr, tt)

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def FindSize(self, dc):
    '''
    Calcula el ancho y alto de la caja
    '''
    s=''.join(self.d) #Obtiene el string
    font, fsize= self.GetFont()
    dc.SetFont(font)
    fmetrics= dc.GetFontMetrics()
    #v=[fmetrics.ascent, fmetrics.descent, fmetrics.height, fmetrics.averageWidth]
    wtext,htext=dc.GetTextExtent(s)
    #Separación del siguiente box
    self.width=wtext+round(fsize//8)
    self.height=htext
    self._ascent=fmetrics.ascent #Altura sobre la linea base
    self._descent=fmetrics.descent #altura bajo la linea base
    self._averageWidth=fmetrics.averageWidth #altura de una x
    self._fsize=fsize
    self._internalLeading=fmetrics.internalLeading # espacio extra superior
    self._externalLeading=fmetrics.externalLeading # espacio entre lineas
    
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DrawBox(self, dc):
    '''
    Dibuja la caja
    '''
    s=''.join(self.d) #Obtiene el string
    font, fsize= self.GetFont()
    dc.SetFont(font)
    dc.DrawText(s,self.gx, self.gy)
    #print('  string dibjado:',s)
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DepureTree(self):
    self.stage=-1 #finaliza
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class InfixBox(Box):
  '''
  Clase abstracta que implementa las operaciones comunes en operadores 
  infijos
  '''
  def __init__(self,root, parent, content=None):
    super(InfixBox,self).__init__(root, parent,content=content)

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def append(self, value, tt=None):
    '''
    value puede ser un toke o un box
    tt indica el tipo de token
    '''
    vr=None #Valor a retornar, si se consume no retorna nada
    if isinstance(value, Box):
      if not value.fullParse:
        raise Exception('  %s: la unidad no se ha finalizado'%(type(self).__name__))
    if not isinstance( value,(str,Box)):
      raise Exception('  %s: el valor a agregar no es una unidad válida'%(type(self).__name__))
    if self.stage ==0:
      # primer parámetro a agregar
      if isinstance(value, str):
        value= StringBox(self.root,self,content=(value,tt))
        value.stage=-1
      value.parent=self
      self.d.append(value)
      self.stage=1
    elif self.stage == 1:
      # Espera el segundo parámetro
      if tt=='c':
        box=StringBox(self.root,self,content=(value,tt))
        box.stage=-1
        self.d.append(box)
        self.stage=-1
        self.parent.endAppend()
      elif tt=='{':
        box=GroupBox(self.root,self)
        self.d.append(box)
        self.root.currentBox=box
        self.stage=2
      else:
        raise Exception('  %s: sintaxis inválida para el exponente'%(type(self).__name__))
    else:
      raise Exception('  %s: en el estado %i no se aceptan valores'%( type(self).__name__,self.stage) )
  
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def  endAppend(self, value=None, tt=None):
    # solo puede finalizar una vez la entrada del exponente
    # con lo cula finaliza la lectura de la potencia
    super(InfixBox,self).endAppend(value,tt)
    self.stage=-1
    self.parent.endAppend()
  
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def FindSize(self, dc):
    '''
    Calcula el ancho y alto de las subcajas, su 
    posicionamiento vertical se da en cada caso particular
    '''
    self.width=0
    print( '  x,y:',(self.x,self.y),'  gx,gy:' ,(self.gx,self.gy))
    # base de la potencia
    self.d[0].fontSizeLvl=self.fontSizeLvl
    self.d[0].fontNormalSize=self.fontNormalSize
    self.d[0].FindSize(dc)
    self.width+=self.d[0].width
    
    #print( '  base gx,gy:',(self.d[0].gx,self.d[0].gy), 
    #  ' parent base:', (self.d[0].parent.gx,self.d[0].parent.gy ) )
    #print(  ' base:',type(self.d[0]).__name__, 
    #  'parent:',type(self.d[0].parent).__name__)
    self._internalLeading=self.d[0]._internalLeading # espacio extra superior
    self._externalLeading=self.d[0]._externalLeading # espacio entre lineas
    self._averageWidth=self.d[0]._averageWidth
    self._ascent=self.d[0]._ascent
    self._descent=self.d[0]._descent
    self._fsize=self.d[0]._fsize
    
    self.d[1].fontSizeLvl=self.fontSizeLvl+1 #suma un nivel
    self.d[1].fontNormalSize=self.fontNormalSize
    self.d[1].FindSize(dc)
    
    if (isinstance(self.d[0],PowBox) and isinstance(self,SubBox) ) or ( 
      isinstance(self.d[0],SubBox) and isinstance(self,PowBox) ):
      self.d[1].x=self.d[0][1].x #Lo que cambia
      
      if self.d[1].width > self.d[0][1].width:
        # la caja es mas ancha, entonces se debe incrementar
        # el ancho de la caja
        self.width+= self.d[1].width-self.d[0][1].width
      #if self.d[1].width > self.d[0]
      #self.width+=self.d[1].width
    else:
      self.d[1].x=self.width
#      self.d[1].fontSizeLvl=self.fontSizeLvl+1 #suma un nivel
#      self.d[1].fontNormalSize=self.fontNormalSize
#      self.d[1].FindSize(dc)
      self.width+=self.d[1].width

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DepureTree(self):
    '''
    Se utiliza para depurar una entrada sin terminar, con el fin de que se pueda
    mostrar
    '''
    if not self.fullParse:
      if len(self.d)== 1:
        if not self.d[0].fullParse:
          self.d[0].DepureTree()
        box=StringBox(self.root,self,content=(' ','c'))
        box.stage=-1
        self.d.append(box)
      elif len(self.d)== 2:
        self.d[1].DepureTree()
      self.stage=-1
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class PowBox(InfixBox):
  def __init__(self,root, parent, content=None):
    super(PowBox,self).__init__(root, parent,content=content)

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def FindSize(self, dc):
    '''
    Calcula el ancho y alto de la caja
    '''
    super(PowBox,self).FindSize(dc)
    #Altura sobre la x 
    ha=self._ascent - self._averageWidth
#    print('')
#    self._printBoxMetrics(head=True)
#    self.d[0]._printBoxMetrics(name='p1   \t')
#    self.d[1]._printBoxMetrics(name='p2   \t')
    
    #Posiciona las dos cajas según el ascent
    if ha > self.d[1]._ascent:
      self.d[1].y=ha-self.d[1]._ascent
    elif ha < self.d[1]._ascent:
      self.d[0].y=self.d[1]._ascent-ha
      self._ascent+=self.d[0].y
      #print('')
    self.height=self._ascent+self._descent
    #print('  p1 x,y:',self.d[0].pos, '  p2 x,y:', self.d[1].pos,'\n')
    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class SubBox(InfixBox):
  '''
  
  '''
  def __init__(self,root, parent,content=None):
    super(SubBox,self).__init__(root, parent,content=content)

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def FindSize(self, dc):
    '''
    Calcula el ancho y alto de la caja
    '''
    #s=''.join(self.d) #Obtiene el string
    super(SubBox,self).FindSize(dc)
    #Altura sobre la x 
    ha=self.d[1]._ascent - self.d[1]._averageWidth
    #Posiciona las dos cajas según el ascent
    self.d[1].y=self._ascent-ha
    descent=self.d[1]._descent+self.d[1]._averageWidth
    if self._descent < descent:
      self._descent= descent
    self.height=self._ascent+self._descent
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Grupos de unidades según los comandos de escape
PREFIJOS={'\\sqrt': SqrtBox, '\\frac':FracBox,'\\int':IntBox}
INFIJOS={'^': PowBox, '_':SubBox}


