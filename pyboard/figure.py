'''
Clase para administrar el dibujo de una figura
'''
import wx
import math
class Figure(object):
  
  
  def __init__(self,tipo, pos=(0,0), width=20, height=20):
    
    self._tipo=tipo
    self.pos=pos
    self.posIni=pos
    self._height=height
    self._width=width
    if tipo == 'circle':
      self._height=width*2
    if len(pos)!=2:
      raise Exception('Error: posición no válida')
    if not tipo in ('circle','rectangle'):
      raise Exception('Error: tipo de figura no válido')
  @property
  def tipo(self):
    return self._tipo

  @property
  def width(self):
    return self._width
  @width.setter
  def width(self,value):
    self._width = value
      
  @property
  def height(self):
    if self.tipo == 'circle':
      return self._width
    return self._height
  
  @height.setter
  def height(self,value):
    self._height = value
  @property
  def rect(self):
    if self.tipo=='rectangle':
      x,y=self.pos
      return wx.Rect(x,y,self.width,self.height)
    return None
  @property
  def radius(self):
    if self.tipo == 'circle':
      return self._width/2
    raise Exception('Error: La figura no tiene radio')
  
  @radius.setter
  def radius(self, value):
    if self.tipo == 'circle':
      self._width=value*2
    else:
      raise Exception('Error: La figura no tiene radio')

  def HitTest(self, pos):
    '''
    Se utiliza para saber si la posición queda dentro de la figura o 
    no, retorna un valor booleano con dicha información.
    '''
    if self.tipo=='circle':
      xc,yc=self.pos
      xc+=self.radius
      yc+=self.radius
      x,y= pos
      rt= round(math.sqrt((x-xc)**2+(y-yc)**2))
      return rt <= self.radius
    if self.tipo=='rectangle':
      x1,y1=self.pos
      x2,y2=self.width+x1,self.height+y1
      # Ordena las coordenadas para comparar
      # sobre un intervalo
      if x1 > x2:
        tmp=x1
        x1=x2
        x2=tmp
      if y1 > y2:
        tmp=y1
        y1=y2
        y2=tmp
      x,y= pos
      return  (x1<=x<=x2) and (y1<= y<= y2)
    return False

  def Draw(self, dc):
    '''
    Dibuja la figura en una contexto de dibujo dado 
    '''
    x,y=self.pos
    if self.tipo == 'circle':
      dc.DrawCircle(x+self.radius,y+self.radius,self.radius)
    elif self.tipo == 'rectangle':
      dc.DrawRectangle(x,y,self.width,self.height)
    else:
      raise Exception('Error: el tipo no es correcto')




