
from .boxs import RootBox #LineBox, PowBox, SubBox, 
from .boxs import PREFIJOS
from .charequ import CHAR_EQ

class FormulaParser(object):
  monoToken='_^+-*/{}()[].,=><'
  def __init__(self, formula):
    self.formula=formula
    self.t=None #token
    self.tt=None #tipo de token

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def Token(self):
    '''
    Generador de tokens
    '''
    c=None
    if self.it< len(self.formula):
      c=self.formula[self.it]
      ic=ord(c)
      self.it+=1
      if 64<ic<91 or 96<ic<123 or 47< ic<58: #Alfanumérico
        pass
      elif c in  self.monoToken:
        pass
      elif c == '\\':
        #Comandos o carácteres de escape
        if self.it < len(self.formula):
          cc=self.formula[self.it]
          ic=ord(cc)
          if ic== 32:
            self.it+=1
            c= '\\ '
          elif ic== ord('{'):
            self.it+=1
            c='\\{'
          elif ic== ord('}'):
            self.it+=1
            c='\\}'
          else:
            while 64<ic<91 or 96<ic<123:#alfabético
              c+=cc
              self.it+=1
              if self.it < len(self.formula):
                cc=self.formula[self.it]
                ic=ord(cc)
              else:
                break
      elif c==' ':
        c=''
    self.t=c
    return c

  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def Parse(self):
    '''
    Construye el arbol semántico 
    '''
    eqchar=False
    t=self.t
    if t == '':
      self.tt=None
      print('  ** Token nulo')
    else:
      if t=='-':
        # esto es para componer símbolost= '̶'
        t='−'
      if len(t) > 1:
        # cambia los comandos de escape de glifos únicos
        tchar=t[1:]
        if tchar in CHAR_EQ:
          t=CHAR_EQ[tchar]
          eqchar=True
      self.t=t
      #Identifica el tipo de token
      tt=None
      if len(t)== 1:
        if t in '{}' and not eqchar:
          tt=t
        elif t in '^_':
          tt='cmd'
        else:
          tt='c' #Tipo de token char
      else:
        tt='cmd'
      if tt != None:
        self.tt=tt
      else:
        raise Exception('  Token no válido: "%s"'%t)
      #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
      self.treeRoot.currentBox.append(self.t,self.tt)
      #print( '  currentBox:', type(self.cu))
  #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def __call__(self, formula=None):
    '''
    Actualiza la fórmula
    '''
    if formula!=None:
      self.formula=formula
      self.it=0
      self.treeRoot=RootBox()
      self.currentBox=self.treeRoot
      i=0
      while self.Token() != None:
        self.Parse()
        #print('  token %i:'%i,self.t, '    tipo:',self.tt)
        #print('  tree:',self.treeRoot)
        #print('  currentBox:',type(self.currentBox).__name__)
        i+=1
         #procesa el token almacenado en self.t
    return self
  


