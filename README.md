# pyboard
Tablero para escribir texto, fórmulas matemáticas y algunas figuras geométricas.

[![pyboard](http://img.youtube.com/vi/Ox3RHDHaz0o/0.jpg)](https://www.youtube.com/watch?v=Ox3RHDHaz0o "Pyboard")

### Contenido
**[Requisitos](#requisitos)**<br>
**[Objetivo de su desarrollo](#objetivo-de-su-desarrollo)**<br>
**[Modo de uso](#modo-de-uso)**<br>

## Requisitos
La aplicación está desarrollada en python 3.7 sobre Linux, y requiere:
* wxpython 4.04

Para instalar un ambiente utilizando anaconda se puede crearlo de la 
siguiente forma:

			$ conda create -n tablero python=3.7 wxpython=4.0.4


## Objetivo de su desarrollo
Esta aplicación fué desarrollada con el fin de presentar una herramienta
para simular un tablero en el que se pueden hacer trazos libremente,
ubicar contenido con bastante libertad.

## Modo de uso
Para iniciar la aplicación, si se cumplen los requisitos basta con 
ubicarse en el directorio de la aplicación, e iniciarla 
desde terminal:

			$ python app.py

Para plataforma Mac se debe utilizar pythonw debido a que requiere utilizar 
ventanas:

			$ pythonw app.py

El diseño de la interfaz es minimalista, carece de menus gráficos, su 
gran mayoria de opciones se ajustan con atajos de teclado. En la barra de 
estado se indica el modo, el texto que se introduce al modo respectivo, y las 
acciones que se ejecutan. Para salir de un modo se utiliza escape, y para 
entrar a un modo se digita su letra respectiva:
  * texto (t): en este modo se ingresa texto linea a linea.
  * fórmulas (f): en este modo se pueden ingresar fórmulas matemáticas en formato
    latex, al momento se soportan los exponentes, subíndices, raíces y fracciones.
    También se pueden escribir símbolos especiales como las letras del alfabeto
    griego, y otros carácteres utf8. En el archivo pyboard/charequ.py se puede
    revisar el listado completo. Es posible pasar del modo fórmula 
    al modo dibujo utilizando TAB.
  * dibujo (d): en este modo se pueden hacer dibujos libres, se pueden activar 
    diferentes herramientas: lápiz (l), polígono (p), goma (g), Cuadrado(C),
    círculo (c), Selección (S). Es posible pasar del modo dibujo 
    al modo fórmula utilizando TAB.

### Modo global
El modo global hace referencia al modo general desde donde se puede acceder 
a los diferentes modos disponibles. Adicional a los modos disponibles hay 
otras funciones en el modo general:
  * presentación (p): abre la ventana de diálogo para seleccionar una carpeta
  donde se hallan imágenes que se pueden utilizar como una presentación.
  * anterior (a): si se tiene una presentación activa, permite regresar al 
   anterior slide.
  * siguiente (s): si se tiene una presentación activa, permite pasar al
  siguiente slide.
  * insertar (i): si se tiene una presentación activa, permite insertar un 
  slide vacío entre el slide actual y el slide siguiente.
  * refrescar (r): si se tiene una presentación activa, permite refrescar la 
  el slide con el contenido original de la presentación.
  
También es posible cambiar los estilos de colores desde el modo global, existen
habilitados 3 estilos utilizando los numeros (1), (2), (3).

### Modo dibujo
En este modo, es posible ajustar el color de los trazos:
  * blanco (b)
  * negro (n)
  * rojo (r)
  * verde (v)
  * azul (z)
  * amarillo (y)
  * cian (x)
  * morado (k)
  * naranja (o)
  * rosa (i)
  * gris (u)
  
Existen acciones particulares en este modo:
  * anterior (a): disminuye el ancho del trazo
  * siguiente (s): aumenta el ancho del trazo
  * finalizar (f): finaliza el trazo de un polígono, así como finaliza  
    el dibujo de un círculo o un rectángulo. Con la herramienta selección,
    permite recortar el área.
  * Finalizar (F): finaliza el trazo de una figura flotante, o con la 
    herramienta selección permite copiar el área que se ha seleccionado. 
  * eliminar (e): elimina toda el área de trabajo, y con la herramienta selección
    elimina la región seleccionada.
  * centrar (0): con el número cero se puede centrar una figura flotante o una
    selección flotante a una posición múltplo de 64.
  * alinear (9): con el número 9 se puede alinear la posición de una figura 
    flotante o una selección flotante a una posición múltplo de 64
  * aumentar (q) y disminuir (w): cuando se tiene una figura flotante se 
    puede aumentar y disminuir su tamaño

Las herramientas de dibujo disponibles son:
  * lápiz (l): permite realizar trazos libres.
  * polígono (p): permite realizar polígonos incertando puntos, para finalizar 
    una secuencia de punos unidos por rectas se utiliza (f). También es posible 
    utilizar  SHIFT como modificador para realizar trazos totalmente horizontales 
    o totalmente verticales.
  * goma (g): permite borrar con el color de fondo, aunque la goma también está 
    disponible en los otros modos con el clic derecho, aunque en este modo es 
    la única forma de ajustar el ancho del trazo de la goma.
  * círculo (c): permite dibujar círculos flotantes, los cuales se pueden dejar
    fijos en el área de trabajo con (f), si se requieren varias copias de un 
    mismo círculo se puede utilizar (F), lo cual dibuja el círculo sin perder 
    la figura flotante que se puede seguir moviendo.
  * Cuadrado (C): permite dibujar rectángulos, y se comporta de modo similar al 
    círculo.
  * Selección (S): mediante un rectángulo flotante indica el área seleccionada. 
    Sobre el área seleccionada se pueden realizar tres operaciones diferentes,
    recortar (f), copiar (F), eliminar (e). Recortar (f) y copiar (F) pasan la 
    región seleccionada a una capa flotante que se puede desplazar y posicionar
    sobre el área de trabajo, si se quiere pegar se puede pasar a realizar 
    otra selección o utilizar (f). 

### Estado flotante
Los diferentes modos generan estados flotantes de contenido, los cuales se 
dibujan sobre el área de trabajo cuando se cambia de modo o se realiza alguna 
acción en particular. Los textos y fórmulas se hallan en estado flotante linea 
a linea, por lo tanto, cuando se digita ENTER se inserta la linea en el área 
de trabajo, en caso contrario la linea está flotante y se puede reposicionar 
clicando en cualquier lugar. De forma similar al texto, funcionan las 
fórmulas. En el modo dibujo se tienen las circunferencias, cuadrados o 
rectángulos y áreas recortadas como elementos flotantes, en este caso particular
los elementos flotantes se pueden mover utilizando las flechas, así como 
tambien se pueden alinear y cambiar de tamaño.

### Deshacer la última acción
Es posible deshacer la última acción que cambie el área de trabajo utilizando CTRL+Z,
por lo cual los elementos flotantes no se pueden alterar al deshacer alguna 
acción.

### Tutorial de ayuda
Se puede acceder al tutorial de ayuda utilizando (p) en modo global y abriendo
la carpeta "help".

![pyboard](https://github.com/carloskl12/pyboard/blob/master/pyboard.png)

