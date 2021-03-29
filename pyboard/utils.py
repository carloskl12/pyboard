import os, time, wx
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# obtiene una lista de archivos segun una extensión:
def getFileList( directorio, tipo):
  '''
  Extensión del fichero, incluye el punto
  '''
  archivos = []
  for root, dirs, files in os.walk(directorio):
    if root == directorio:
      for filename in files:
        fnOnly, file_extension = os.path.splitext(filename)
        if file_extension == tipo:
          archivos.append(filename)

  archivos.sort()
  return archivos
  


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Slides(object):
  '''
  Clase para administrar los slides a mostrar, el modo de trabajar con slides
  es que puede existir un conjunto de slides de fondo (slidesBg), sobre el 
  cual se puede modificar con las herramientas del programa, y que si en 
  algún momento se quiere la imagen original es posible hacer un refrescar (r)
  para volver a la imágen de fondo.
  
  
  * chalkboard: directorio donde guardar los resultados
  * bmpDraw: es el mapa de bits donde se dibujará el slide actual
  * bgBoardColour: color del fondo
  * sbHeight: status bar height
  * name: nombre de la carpeta que contendrá los resultados, si no se 
    da, se genera un nombre con la fecha y hora.
  * dirslides: directorio donde están las imágenes de una presentación
    que se utilizará de fondo
  '''
  def __init__(self,chalkboard, bmpDraw, bgBoardColour, sbHeight, name=None, dirslidesBg=None):
    '''
    Genera la carpeta por defecto donde se guarda la actividad
    de la sesión actual, para ello usa el nombre según la fecha
    y hora
    '''
    
    self._bmpDraw=bmpDraw
    self._bgBoardColour=bgBoardColour
    self.sbHeight=sbHeight
    # guarda los slides
    self._slides=[]
    if name == None:
      # Si no hay nombre para la presentación, se genera un nombre 
      # con la fecha actual
      stime= time.strftime("%b_%d_%Y(%H_%M_%S)", time.localtime())
      self._chkbfname=os.path.join(chalkboard,stime)
    else:
      self._chkbfname=os.path.join(chalkboard,name)
    
    if os.path.isdir(self._chkbfname):
      chkbfname=self._chkbfname
      n=0
      while os.path.isdir(chkbfname+'_'+str(n)):
        n+=1
      
#      # si el directorio de la presentación ya existe 
#      # Se carga y se guarda en slides
#      slideFiles=getFileList(self._chkbfname,'.png')
#      self._slides=[ (name, None) for name in slideFiles]
      print('Warning: The directory "%s" already exists'%self._chkbfname)
      self._chkbfname=chkbfname+'_'+str(n)
    #else:
    # Siempre se crea un directorio de la presentación
    os.makedirs(self._chkbfname)
    
    self._dirslidesBg=dirslidesBg #directorios de los fondos
    self._slidesBg=[] #Almacena los nombres de las imágenes
    
    slideBg=None
    if dirslidesBg !=None:
      # Se cargan los slides de fondo que deben estar 
      # en un directorio diferente al del chalkboard
      basename=os.path.basename(os.path.normpath(dirslidesBg))
      self._dirslidesBg=dirslidesBg
      pngs=getFileList(dirslidesBg,'.png')
      jpgs=getFileList(dirslidesBg,'.jpg')
      self._slidesBg= pngs+jpgs
      if len(self._slidesBg)>0 and len(self._slides) == 0:
        # Si hay slides de fondo, y no hay ningún slide 
        # dentro del directorio de chalkboard, procede 
        # a dibujar el fondo
        slideBg=self._slidesBg[0]
        fname= os.path.join(self._dirslidesBg, slideBg)
        self.DrawFile(fname)
    
    # Se verifica si


    if len(self._slides) > 0 :
      # Si hay slides, se dibuja el primero 
      slidename,slideBgname=self._slides[0]
      fname= os.path.join(self._chkbfname,slidename)
      self.DrawFile(fname)
    # Almacena parejas ( slidename, slidesBg ), si no hay slidesBg se guarda un
    # None, es útil para saber si hay o no imágen para refrescar en caso que 
    # el usuario lo requiera
    self._islide=0 #Indice del slide actual
    self._islideBg=0 #indice sobre los slides de bg
    #slidefnames=(self.GetSlideName,None)
    
    if len(self._slides)>0:
      # Agrega los nombres de los slides de fondo (slideBg) 
      # a la lista self._slidesBg
      tmp=[]
      i=0
      for slidename, v in self._slides:
        slideBgname=None
        if i < len(self._slidesBg):
          slideBgname=self._slidesBg[i]
        tmp.append((slidename,slideBgname))
        i+=1
      self._slides=tmp
    else:
      self._slides=[(self.GetSlideName(), slideBg)]
    
  def SetBackgroundColour(self, colour):
    self._bgBoardColour= colour
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def SaveSlide(self):
    '''
    Guarda el bitmap actual con el nombre correcto en el directorio 
    _chkbfname
    
    '''
    slidename, slidesBg= self._slides[self._islide]
    #name=slidename+'.png'
    fname= os.path.join(self._chkbfname, slidename)
    self._bmpDraw.SaveFile(fname, wx.BITMAP_TYPE_PNG)
  
  def GetSlideName(self):
    '''
    Retorna el nombre del slide actual
    '''
    return 'diap_{num:04d}.png'.format(num=self._islide)

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def Next(self):
    '''
    Actualiza al siguiente slide
    '''
    if not self.SetSlide(self._islide+1): #SetSlide debió guardar
      # Quiere decir que no hay mas diapositivas
      # por tanto crea una nueva limpiando lo que hay actualmente
      self._islideBg+=1
      self._islide+=1
      slideBg=None
      slidename=self.GetSlideName()
      self._slides.append( (slidename,slideBg) )
      #Borra lo que hay actualmente
      dc = wx.MemoryDC()
      dc.SelectObject(self._bmpDraw)
      #ancho, alto = self._bmpDraw.GetSize()
      #alto=alto-self.sbHeight
      dc.SetBackground(wx.Brush(self._bgBoardColour))
      dc.Clear()
    return self._islide
  
  def Previus(self):
    if self._islide > 0: #Para ahorrar tiempo en guardado no necesario al llegar al inicio
      self.SetSlide(self._islide-1)
    return self._islide

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def SetSlide(self, index):
    '''
    Actualiza el slide actual
    '''
    fname= None
    # Carga un slide que ya existe
    # Guarda el valor actual
    self.SaveSlide()
    slidename, slideBg= 0,0
     
    if 0 <= index < len(self._slides) :
      slidename, slideBg= self._slides[index]
      fname=os.path.join(self._chkbfname, slidename)
      self._islide=index
      # Actualiza el índice del slide de fondo
      if isinstance (slideBg,str):
        #Si es string se busca su respectivo índice
        self._islideBg=self._slidesBg.index(slideBg)
      elif isinstance(slideBg,int):
        #Si es entero será el índice
        self._islideBg=slideBg
    elif 0<=  (self._islideBg +1) < len(self._slidesBg):
      #No se ha trabajado aún, pero el slide siguiente de fondo existe
      self._islideBg+=1
      self._islide+=1
      slideBg=self._slidesBg[self._islideBg]
      slidename=self.GetSlideName()
      fname= os.path.join(self._dirslidesBg, slideBg)
      self._slides.append( (slidename,slideBg) )
    
    if fname !=None:
      self.DrawFile(fname)
      return True
    else:
      print('  no se pudo dibujar', len(self._slides))
      return False
    return self._islide
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def DrawFile(self, filename):
    '''
    Dibuja el bitmap dado un filename
    '''
    #print('  slides -- bgBoardColour:', self._bgBoardColour)
    dc = wx.MemoryDC()
    dc.SelectObject(self._bmpDraw)
    ancho, alto = self._bmpDraw.GetSize()
    alto=alto-self.sbHeight
    dc.SetBackground(wx.Brush(self._bgBoardColour))
    dc.Clear()
    bitmap=wx.Bitmap(filename)
    w,h= bitmap.GetSize()
    x=0
    y=0
    if ancho > w:
      x= (ancho-w)//2
    if alto > h:
      y= (alto-h)//2
    dc.DrawBitmap(bitmap,x,y)
    
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def Refresh(self):
    '''
    Refresca con el slide de fondo si existe
    '''
    slidename, slideBg= self._slides[self._islide]
    if isinstance(slideBg,str):
      fname= os.path.join(self._dirslidesBg, slideBg)
      self.DrawFile(fname)
      return True
    return False
  
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def Instert(self):
    '''
    Inserta un slide en blanco
    '''
    self.SaveSlide()
    self._islide+=1
    slideBg=self._islideBg
    if len(self._slidesBg)==0:
      slideBg=None
    slidename=self.GetSlideName()
    if len(self._slides)>self._islide:
      # Hay slides adelante por tanto se deben renombrar
      renombrar= [sld for sld in self._slides[self._islide:]]
      # Guarda el numero de slide
      tmp=self._islide
      self._islide=len(self._slides)
      # Inicia desde el final para no sobreescribir algun 
      # archivo ya existente
      renombrados=[]
      for name, other in renombrar[::-1]:
        slidename=self.GetSlideName()
        newfname= os.path.join(self._chkbfname, slidename)
        oldfname= os.path.join(self._chkbfname,name)
        os.rename(oldfname,newfname)
        renombrados.append((slidename,other))
        self._islide-=1
      renombrados.append( (self.GetSlideName(),None))
      self._slides=self._slides[:self._islide]+renombrados[::-1]
    else:
      self._slides.append( (slidename,slideBg) )
    #Borra lo que hay actualmente
    dc = wx.MemoryDC()
    dc.SelectObject(self._bmpDraw)
    ancho, alto = self._bmpDraw.GetSize()
    alto=alto-self.sbHeight
    dc.SetBackground(wx.Brush(self._bgBoardColour))
    dc.Clear()
    print('  slides:',self._slides)
    return self._islide
