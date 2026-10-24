import cv2
import numpy as np
import parte_1 as parte1
from svgpathtools import svg2paths

#Leemos la primera imagen para obtener su tamaño. Ese tamaño se utilizará para generar el video writer.
img = cv2.imread("./datos/imagenes/img_001.jpg") 
size = (img.shape[1], img.shape[0])

#Configurar las opciones: proyectar un cuadrado o un svg
print("Selecciona una opción:")
print("1. Proyectar cuadrado ")
print("2. Proyectar svg")
opcion = input("Elige una opción: ")

#Definimos el video, su nombre, frames, codificador y tamaño
if opcion == "1":
    out_mp4 = cv2.VideoWriter("resultados/parte2.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 30, size)
elif opcion == "2":
    out_mp4 = cv2.VideoWriter("resultados/parte2_svg.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 30, size)

#Definir el pattern size que se le pasará a la funcion findChessboardCorners. 
# (numero de vertices internos que tiene por filas y columnas)
patternSize = (9, 6)

#Obtener las coordenadas de los vértices internos.
coordPlano = np.load("lag/coordPlano.npy")


if opcion == "1":
    #Definimos los puntos de nuestro cuadrado, y las convertimos a coordenadas homogeneas
    punto1Cuadrado = (4, 8, 1)
    punto2Cuadrado = (12, 8, 1)
    punto3Cuadrado = (12, 0, 1)
    punto4Cuadrado = (4, 0, 1)
elif opcion=="2":
    svg_path = "./datos/gato.svg"
    #Asignar cuantos puntos por cada linea procesaremos
    num_puntos = 200 # Cuanto mas alto este numero mayor la precisión
    paths, attributes = svg2paths(svg_path)
    puntos_svg = []
    for path in paths:
        for i in range(num_puntos + 1):
            punto = path.point(i / num_puntos) #Obtener el punto del camino
            puntos_svg.append((punto.real, punto.imag)) #real  x, imag  y


    #Datos obtenidos desde el xml
    svg_width = 1279
    svg_height = 1280
    
    
    #normalizar los puntos para que puedan entrar en nuestra imagen
    puntos_svg_normalizados = [(x / svg_width, y / svg_height) for (x, y) in puntos_svg]
    puntosNormalizados = []

#Iteramos por cada frame
for fileIndex in range(1, 736):

    #Leer datos de la imagen
    img = cv2.imread(f"./datos/imagenes/img_{fileIndex:03d}.jpg") 
 
    #Obtener las coordenadas de los vertices internos.
    encontrado, corners = cv2.findChessboardCorners(img, patternSize)

    #Lista que guardará los vértices del ajedrez reformateados. 
    imageCornersClean = []

    #Si la función ha encontrado los puntos, dibujarlos
    if(encontrado):
        #Iterar en los vértices encontrados
        for i in range(1, corners.shape[0] + 1):
            imageCornersClean.append([int(corners[i-1][0][0]), int(corners[i-1][0][1])])

        #Convertir la lista a np array
        imageCornersClean = np.array(imageCornersClean)

        #Encontrar homografia
        homografia = parte1.findHomography(coordPlano, imageCornersClean)
        img_linea = img.copy()


        if opcion=="1":
            #Aplicamos la homografía a las coordenadas y las pasamos al plano euclideo
            p1CTransformado = np.dot(homografia, punto1Cuadrado)
            p1CTNormalizado = (p1CTransformado[0]/p1CTransformado[2], p1CTransformado[1]/p1CTransformado[2])
            p2CTransformado = np.dot(homografia,punto2Cuadrado)
            p2CTNormalizado = (p2CTransformado[0]/p2CTransformado[2], p2CTransformado[1]/p2CTransformado[2])
            p3CTransformado = np.dot(homografia,punto3Cuadrado)
            p3CTNormalizado = (p3CTransformado[0]/p3CTransformado[2], p3CTransformado[1]/p3CTransformado[2])
            p4CTransformado = np.dot(homografia,punto4Cuadrado)
            p4CTNormalizado = (p4CTransformado[0]/p4CTransformado[2], p4CTransformado[1]/p4CTransformado[2])

            #Dibujamos las lineas
            cv2.line(img_linea, (int(p1CTNormalizado[0]),int(p1CTNormalizado[1])), (int(p2CTNormalizado[0]),int(p2CTNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(img_linea, (int(p2CTNormalizado[0]),int(p2CTNormalizado[1])), (int(p3CTNormalizado[0]),int(p3CTNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(img_linea, (int(p3CTNormalizado[0]),int(p3CTNormalizado[1])), (int(p4CTNormalizado[0]),int(p4CTNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(img_linea, (int(p4CTNormalizado[0]),int(p4CTNormalizado[1])), (int(p1CTNormalizado[0]),int(p1CTNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
        
        elif opcion=="2":

            for j in range(len(puntos_svg_normalizados)-1):
                # Calcular primer punto
                p1 = np.array([puntos_svg_normalizados[j][0], puntos_svg_normalizados[j][1], 1.0])
                p1Transf = np.dot(homografia, p1)
                p1Norm = (p1Transf[0]/p1Transf[2], p1Transf[1]/p1Transf[2])
                
                # Calcular segundo punto
                p2 = np.array([puntos_svg_normalizados[j+1][0], puntos_svg_normalizados[j+1][1], 1.0])
                p2Transf = np.dot(homografia, p2)
                p2Norm = (p2Transf[0]/p2Transf[2], p2Transf[1]/p2Transf[2])
                
                # Dibujar la línea entre los dos puntos
                cv2.line(img_linea, 
                        (int(p1Norm[0]), int(p1Norm[1])), 
                        (int(p2Norm[0]), int(p2Norm[1])),
                        (142, 0, 255), thickness=1, lineType=cv2.LINE_AA)
        #Añadimos el frame editado al video
        out_mp4.write(img_linea)


    else:
        #Si no se encuentra el ajedrez, añadimos el frame sin editar al video
        out_mp4.write(img)

out_mp4.release()