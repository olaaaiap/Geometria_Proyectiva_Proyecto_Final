## Estructura del proyecto:

El proyecto se divide en 4 scripts (parte_1.py, parte2.py, parte3.py y parte4.py), y 3 carpetas: datos (datos del proyecto), resultados (resultados obtenidos, nombrados como se ha pedido en el enunciado) y lag (que contiene el archivo coordPlano.npy - la lista de los vértices en mi plano del ajedrez).

En los scripts se pueden identificar los diferentes ejercicios fácilmente (################### PRIMER EJERCICIO ################### etc.), y todas la líneas están debidamente comentadas. 
En el código también se podrán ver  comentarios con la palabra "DESCOMENTAR". Estos comentarios se han añadido en los print que he utilizado para analizar ciertos valores que he obtenido durante el proceso.


## Como ejecutar los scripts:

La ejecución de los scripts se debe hacer en orden para asegurarnos que coordPlano.npy está generado. Por otro lado, en la parte 1, 2 y 4 se pedirá escoger entre la opción 1 (dibujar un cuadrado o un cubo) y la opción 2 (dibujar un svg o un .obj). El usuario podrá escoger el que prefiera. 


## Referencias

- **SvgToPath()**: https://pypi.org/project/svgpathtools/
- **drawFrameAxes()**: https://shimat.github.io/opencvsharp_docs/html/3baec2d3-bb00-26ff-75a9-be6857745d08.htm
- **Estructura .obj**: https://docs.fileformat.com/es/3d/obj/
