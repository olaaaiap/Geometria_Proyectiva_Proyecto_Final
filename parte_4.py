import cv2
import numpy as np
import parte_1 as parte1

##################################### FUNCIONES AUXILIARES #####################################

#Función para leer archivo .obj
def leerObj():
    file = open("./datos/avion.obj")
    coordenadas = []
    for line in file.readlines():
        #Si la linea empieza con v, es la definición de un vértice
        if(line.startswith("v ")):
            lineArray = line.split(" ")[2:]
            coordenadas.append([float(lineArray[0]), float(lineArray[1]), float(lineArray[2].replace("\n","")) ])
    return coordenadas

##################################### END FUNCIONES AUXILIARES #################################



# Definir el video writer
img = cv2.imread("./datos/imagenes/img_001.jpg") 
size = (img.shape[1], img.shape[0])

#Configurar las opciones: proyectar un cuadrado o un svg
print("Selecciona una opción:")
print("1. Proyectar cubo ")
print("2. Proyectar obj")
opcion = input("Elige una opción: ")

#Definimos el video, su nombre, frames, codificador y tamaño
if opcion == "1":
    out_mp4 = cv2.VideoWriter("resultados/parte4.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 30, size)
elif opcion == "2":
    out_mp4 = cv2.VideoWriter("resultados/parte4_obj.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 30, size)


patternSize = (9, 6)

#Obtener las coordenadas de los vértices internos.
coordPlano = np.load("lag/coordPlano.npy")

if opcion == "1":
    #Definimos los puntos de nuestro cuadrado, y las convertimos a coordenadas homogeneas
    cuadrado = 4
    #Base
    punto1 = [cuadrado,cuadrado,0,1]
    punto2 = [3*cuadrado,cuadrado,0,1]
    punto3 = [3*cuadrado,3*cuadrado,0,1]
    punto4 = [cuadrado,3*cuadrado,0,1]
    #Tapa
    punto5 = [cuadrado,cuadrado,cuadrado*2,1]
    punto6 = [3*cuadrado,cuadrado,cuadrado*2,1]
    punto7 = [3*cuadrado,3*cuadrado,cuadrado*2,1]
    punto8 = [cuadrado,3*cuadrado,cuadrado*2,1]
elif opcion=="2":
    #Leer archivo
    coordenadasObj = leerObj()

#Obtener matriz intrínseca K.
K = np.loadtxt("./datos/K.txt") 

#Escala que aplicaremos al objeto
scale = 0.005


#Iteramos por cada frame
for fileIndex in range(1, 736):
    puntosNormalizados = []
    #Leer datos de la imagen
    img = cv2.imread(f"./datos/imagenes/img_{fileIndex:03d}.jpg") 
    encontrado, corners = cv2.findChessboardCorners(img, patternSize)

    imageCornersClean = []

    if(encontrado):
        #Utilizamos shape[0] para obtener la cantidad de puntos a dibujar
        for i in range(1, corners.shape[0] + 1):
            imageCornersClean.append([int(corners[i-1][0][0]), int(corners[i-1][0][1])])

        imageCornersClean = np.array(imageCornersClean)

        
        #Buscar homografía
        homografia = parte1.findHomography(coordPlano, imageCornersClean)
        
        ############################## OBTENER R ##############################
        #Calcular matriz M
        #M = K^-1 H
        K_inv = np.linalg.inv(K)
        M = np.dot(K_inv, homografia)

        #Obtener las primeras 2 columnas de M
        M_prima = M[:, :2]

        #Aplicar SVD para obtener la descomposición
        U_prima, S_prima, Vt_prima = np.linalg.svd(M_prima, full_matrices=False)

        #R* = U Vt
        R_star = np.dot(U_prima, Vt_prima)

        #Calcular lambda
        factorLambdaFinal = np.trace(np.dot(R_star.T, M_prima)) / np.trace(np.dot(M_prima.T, M_prima))

        r3_star = np.cross(R_star[:, 0], R_star[:, 1])
        R = np.column_stack((R_star, r3_star))
        t = M[:, 2] * factorLambdaFinal

        ############################## OBTENER P ##############################
        #P = K[R|t]
        R_t = np.column_stack((R, t))
        P = np.dot(K, R_t)

        if opcion == "1":
            #Calcular la proyección de los puntos del cubo
            punto1Transformado = np.dot(P, punto1)
            punto1TNormalizado = (punto1Transformado[0]/punto1Transformado[2], punto1Transformado[1]/punto1Transformado[2])

            punto2Transformado = np.dot(P, punto2)
            punto2TNormalizado = (punto2Transformado[0]/punto2Transformado[2], punto2Transformado[1]/punto2Transformado[2])

            punto3Transformado = np.dot(P, punto3)
            punto3TNormalizado = (punto3Transformado[0]/punto3Transformado[2], punto3Transformado[1]/punto3Transformado[2])

            punto4Transformado = np.dot(P, punto4)
            punto4TNormalizado = (punto4Transformado[0]/punto4Transformado[2], punto4Transformado[1]/punto4Transformado[2])

            punto5Transformado = np.dot(P, punto5)
            punto5TNormalizado = (punto5Transformado[0]/punto5Transformado[2], punto5Transformado[1]/punto5Transformado[2])

            punto6Transformado = np.dot(P, punto6)
            punto6TNormalizado = (punto6Transformado[0]/punto6Transformado[2], punto6Transformado[1]/punto6Transformado[2])

            punto7Transformado = np.dot(P, punto7)
            punto7TNormalizado = (punto7Transformado[0]/punto7Transformado[2], punto7Transformado[1]/punto7Transformado[2])

            punto8Transformado = np.dot(P, punto8)
            punto8TNormalizado = (punto8Transformado[0]/punto8Transformado[2], punto8Transformado[1]/punto8Transformado[2])

            puntos_proj = [punto1TNormalizado, punto2TNormalizado, punto3TNormalizado, punto4TNormalizado, punto5TNormalizado, punto6TNormalizado, punto7TNormalizado, punto8TNormalizado]

            #Dibujamos las lineas
            frame_copy = img.copy()
            cv2.line(frame_copy, (int(punto1TNormalizado[0]),int(punto1TNormalizado[1])), (int(punto2TNormalizado[0]),int(punto2TNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(frame_copy, (int(punto2TNormalizado[0]),int(punto2TNormalizado[1])), (int(punto3TNormalizado[0]),int(punto3TNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(frame_copy, (int(punto3TNormalizado[0]),int(punto3TNormalizado[1])), (int(punto4TNormalizado[0]),int(punto4TNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(frame_copy, (int(punto4TNormalizado[0]),int(punto4TNormalizado[1])), (int(punto1TNormalizado[0]),int(punto1TNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea

            cv2.line(frame_copy, (int(punto5TNormalizado[0]),int(punto5TNormalizado[1])), (int(punto6TNormalizado[0]),int(punto6TNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(frame_copy, (int(punto6TNormalizado[0]),int(punto6TNormalizado[1])), (int(punto7TNormalizado[0]),int(punto7TNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(frame_copy, (int(punto7TNormalizado[0]),int(punto7TNormalizado[1])), (int(punto8TNormalizado[0]),int(punto8TNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(frame_copy, (int(punto8TNormalizado[0]),int(punto8TNormalizado[1])), (int(punto5TNormalizado[0]),int(punto5TNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea

            cv2.line(frame_copy, (int(punto1TNormalizado[0]),int(punto1TNormalizado[1])), (int(punto5TNormalizado[0]),int(punto5TNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(frame_copy, (int(punto2TNormalizado[0]),int(punto2TNormalizado[1])), (int(punto6TNormalizado[0]),int(punto6TNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(frame_copy, (int(punto3TNormalizado[0]),int(punto3TNormalizado[1])), (int(punto7TNormalizado[0]),int(punto7TNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(frame_copy, (int(punto4TNormalizado[0]),int(punto4TNormalizado[1])), (int(punto8TNormalizado[0]),int(punto8TNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
        elif opcion=="2":
            #Calcular la proyección de los puntos del objeto
            prev = None #Para empezar a dibujar las lineas cuando estemos procesando la segunda
            frame_copy = img.copy()
            for j in range(0, len(coordenadasObj)):
                # Aplicar escala a la coordenada, trasladarla (x+16 y y+8) y crear la coordenada homogenea
                puntoObj = np.array([(coordenadasObj[j][0] *scale)+16  , (coordenadasObj[j][1] *scale) +8, coordenadasObj[j][2] *scale , 1.0])
                # Aplicar proyección
                pTransf = np.dot(P, puntoObj)
                # Pasar al plano euclideo
                pNorm = (pTransf[0]/pTransf[2], pTransf[1]/pTransf[2])
                puntosNormalizados.append(pNorm)
                if prev != None:
                    cv2.line(frame_copy, (int(prev[0]), int(prev[1])), (int(pNorm[0]),int(pNorm[1])), (142, 0, 255), thickness=1,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
                prev = pNorm

        #Añadimos el frame editado al video
        out_mp4.write(frame_copy)


    else:
        #Si no se encuentra el ajedrez, añadimos el frame sin editar al video
        out_mp4.write(img)

out_mp4.release()