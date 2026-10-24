import cv2
import numpy as np
from svgpathtools import svg2paths


##################################### FUNCIONES AUXILIARES #####################################
homografias = []
def findHomography(srcPoints, dstPoint):
    #Direct Linear Transformation:
    #Construir la matriz A desde todas las correspondencias srcPoints - dstPoints
    matrizA = []
    # Como srcPoints y dstPoints tienen la misma longitud, iterar sobre la longitud de srcPoints
    for i in range(0, len(srcPoints)):
        #Obtener "u" y "v"
        u_a = srcPoints[i][0]
        v_a = srcPoints[i][1]
        u_b = dstPoint[i][0]
        v_b = dstPoint[i][1]
        #Cada correspondencia generará 2 restricciones sobre h.
        #Crearlas y añadirlas a la matriz A
        matrizA.append([u_a, v_a, 1, 0, 0, 0, -u_a*u_b, -v_a*u_b, -u_b])
        matrizA.append([0, 0, 0, u_a, v_a, 1, -u_a*v_b, -v_a*v_b, -v_b])
    
    #Singular Value Decomposition
    #Obtener la SVD de A
    _, S, Vt = np.linalg.svd(matrizA)
    np.set_printoptions(suppress=True, precision=4) #Cambiar el estilo de print para ver los valores a 4 decimales
    
    
    # DESCOMENTAR para ver la matriz S
    # print("Matriz S:", S, "\n\n\n")

    #La diagonal de S es 21665.4244, 14.5669, 0.01; 
    # Por tanto, la diagonal de S esta compuesta por valores positivos en orden descendente.
    # En conclusión: h es igual a la última columna de V

    #Como tenemos la traspuesta de V, tenemos que coger su última fila, no su última columna
    ultima_col  = Vt[-1, :]
    
    #Pasar ultima_col de un array de 1D a una matriz de 2D
    H_ba = ultima_col.reshape((3, 3))
    
    #h9 tiene que ser 1, por tanto, obtenemos su valor y dividimos todos los elementos de la matriz por ese valor
    h9 = H_ba[2][2]
    H_ba_final = H_ba / h9
    return H_ba_final

##################################### END FUNCIONES AUXILIARES #################################



############################################################################################
##################################### PRIMER EJERCICIO #####################################
############################################################################################

if __name__ == "__main__":
    #Leer datos de la imagen y hacer una copia para dibujar los vértices internos
    img = cv2.imread("./datos/imagenes/img_001.jpg") 
    img_copy = img.copy()


    #Definir el pattern size que se le pasará a la funcion findChessboardCorners. 
    # (numero de vértices internos que tiene por filas y columnas)
    patternSize = (9, 6)

    #Obtener las coordenadas de los vértices internos.
    #encontrado: booleano que nos dirá si la imagen se ha podido interpretar y si se han obtenido los puntos correctamente
    # corners: matriz de 3 dimensiones con las coordenadas de cada punto. 
    #   Ejemplo: 
    #       print(corners[0]) 
    #       output: [[239.757    96.40928]]
    encontrado, corners = cv2.findChessboardCorners(img, patternSize)

    #Definir un color para dibujar los puntos obtenidos en la imagen
    color_puntos = 255, 0, 242

    #Lista que guardará los vértices del ajedrez reformateados. 
    # Este array hace falta ya que findChessboardCorners devuelve una lista con formato [[[x1, y1]], [[...]] ...]
    imageCornersClean = []
   
    #Si la función ha encontrado los puntos, dibujarlos
    if(encontrado):
        #Iterar en los vértices encontrados
        for i in range(1, corners.shape[0] + 1):
            #Aumentamos el thickness en cada punto para saber en que dirección van las coordenadas
            cv2.circle(img_copy, (int(corners[i-1][0][0]), int(corners[i-1][0][1])), 0, (color_puntos), thickness=int(4+i/2), lineType=cv2.LINE_AA)
            
            #Añadimos el punto formateado en nuestra lista
            imageCornersClean.append([int(corners[i-1][0][0]), int(corners[i-1][0][1])])

        # DESCOMENTAR si se quiere ver los puntos encontrados por findChessboardCorners
        # cv2.imshow("Imagen del ajedrez con puntos", img_copy)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        #Convertir la lista a np array
        imageCornersClean = np.array(imageCornersClean)

        
        #El primer punto que nos devuelve findChessboardCorners está ubicado arriba a la izquierda, pero nuestro sistema de
        # referencia empieza abajo a la izquierda. Por tanto, vamos a crear una lista con las coordenadas en nuestro sistema,
        # pero empezando desde arriba. 
        # Ejemplo: el primer elemento de la lista coordPlano será (0,5)
        coordPlano = []
        for j in range(6, 0, -1):
            for i in range(1, 10):
                coordPlano.append([(i-1)*4, (j-1)*4])
        coordPlano = np.array(coordPlano)
        np.save("lag/coordPlano.npy", coordPlano)


        #Una vez que tenemos los vértices en el mismo orden, podemos llamar a findHomography
        homografia = findHomography(coordPlano, imageCornersClean)

        # DESCOMENTAR para comparar la homografía calculada a con la real
        # homografiaReal, status = cv2.findHomography(coordPlano, imageCornersClean)
        # print (homografiaReal)
        # print (homografia)

        #Guardar la matriz de homografía
        np.savetxt('resultados/parte1_H.txt', homografia)

        #Configurar las opciones: proyectar un cuadrado o un svg
        print("Selecciona una opción:")
        print(" 1. Proyectar cuadrado ")
        print(" 2. Proyectar svg\n")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            ############################################################################################
            ##################################### SEGUNDO EJERCICIO ####################################
            ############################################################################################
            
            #Definimos los puntos de nuestro cuadrado, y las convertimos a coordenadas homogeneas
            punto1Cuadrado = (4, 8, 1)
            punto2Cuadrado = (12, 8, 1)
            punto3Cuadrado = (12, 0, 1)
            punto4Cuadrado = (4, 0, 1)

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
            img_linea = img.copy()
            cv2.line(img_linea, (int(p1CTNormalizado[0]),int(p1CTNormalizado[1])), (int(p2CTNormalizado[0]),int(p2CTNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(img_linea, (int(p2CTNormalizado[0]),int(p2CTNormalizado[1])), (int(p3CTNormalizado[0]),int(p3CTNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(img_linea, (int(p3CTNormalizado[0]),int(p3CTNormalizado[1])), (int(p4CTNormalizado[0]),int(p4CTNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(img_linea, (int(p4CTNormalizado[0]),int(p4CTNormalizado[1])), (int(p1CTNormalizado[0]),int(p1CTNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.imwrite("resultados/parte1_2.png", img_linea)
            cv2.imshow("Imagen del ajedrez con cuadrado",img_linea)
            cv2.waitKey(0)

            ############################################################################################
            ##################################### TERCER EJERCICIO ####################################
            ############################################################################################

            #Definimos nuestros puntos en el plano, ahora eligiendo puntos entre 2 vértices
            punto1Cuadrado = (6, 10, 1)
            punto2Cuadrado = (14, 10, 1)
            punto3Cuadrado = (14, 2, 1)
            punto4Cuadrado = (6, 2, 1)

            #Aplicamos la homografía a las coordenadas y las pasamos al plano euclideo
            p1CTransformado = np.dot(homografia, punto1Cuadrado)
            p1CTNormalizado = (p1CTransformado[0]/p1CTransformado[2], p1CTransformado[1]/p1CTransformado[2])
            p2CTransformado = np.dot(homografia, punto2Cuadrado)
            p2CTNormalizado = (p2CTransformado[0]/p2CTransformado[2], p2CTransformado[1]/p2CTransformado[2])
            p3CTransformado = np.dot(homografia, punto3Cuadrado)
            p3CTNormalizado = (p3CTransformado[0]/p3CTransformado[2], p3CTransformado[1]/p3CTransformado[2])
            p4CTransformado = np.dot(homografia, punto4Cuadrado)
            p4CTNormalizado = (p4CTransformado[0]/p4CTransformado[2], p4CTransformado[1]/p4CTransformado[2])


            #Dibujamos las lineas
            img_linea = img.copy()
            cv2.line(img_linea, (int(p1CTNormalizado[0]),int(p1CTNormalizado[1])), (int(p2CTNormalizado[0]),int(p2CTNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(img_linea, (int(p2CTNormalizado[0]),int(p2CTNormalizado[1])), (int(p3CTNormalizado[0]),int(p3CTNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(img_linea, (int(p3CTNormalizado[0]),int(p3CTNormalizado[1])), (int(p4CTNormalizado[0]),int(p4CTNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.line(img_linea, (int(p4CTNormalizado[0]),int(p4CTNormalizado[1])), (int(p1CTNormalizado[0]),int(p1CTNormalizado[1])), (0,255,255), thickness=5,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.imwrite("resultados/parte1_3.png", img_linea)
            cv2.imshow("Imagen del ajedrez con cuadrado",img_linea)
            cv2.waitKey(0)
        elif opcion == "2":
            #Obtener svg
            svg_path = "./datos/gato.svg"
            #Asignar cuantos puntos por cada linea procesaremos
            num_puntos = 200 # Cuanto mas alto este numero mayor la precisión

            #Aplicar svg2paths de svgpathtools para obtener los caminos o lineas del svg
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
            puntosTransformados = []
            
            for j in range(0, len(puntos_svg_normalizados)):
                #Escalar el punto para que entre en el ajedrez
                pEscalado = np.array([puntos_svg_normalizados[j][0] , puntos_svg_normalizados[j][1] , 1.0])
                #Aplicar homografia
                pTransf = np.dot(homografia, pEscalado)
                #Pasar el punto al plano euclideo
                pNorm = (pTransf[0]/pTransf[2], pTransf[1]/pTransf[2])
                puntosTransformados.append(pNorm)

            img_linea = img.copy()
            for k in range(0, len(puntosTransformados)-1):
                #Dibujamos las lineas
                cv2.line(img_linea, (int(puntosTransformados[k][0]),int(puntosTransformados[k][1])), (int(puntosTransformados[k+1][0]),int(puntosTransformados[k+1][1])), (142, 0, 255), thickness=1,lineType=cv2.LINE_AA) #en que imagen; donde empieza; donde acaba; color; thickness; estilo de la linea
            cv2.imwrite("resultados/parte1_2_svg.png", img_linea)
            cv2.imshow("Imagen del ajedrez con cuadrado",img_linea)
            cv2.waitKey(0)
    else:
        print("No se podido interpretar el ajedrez de la imagen.")




