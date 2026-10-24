import cv2
import numpy as np

#Obtener matriz intrínseca K. Utilizamos loadtxt para que interprete las matrices
K = np.loadtxt("./datos/K.txt") 
#Obtener matriz de homografía H
H = np.loadtxt("./resultados/parte1_H.txt") 


############################################################################################
##################################### PRIMER EJERCICIO #####################################
############################################################################################

#Calcular matriz M
#M = K^-1 H
K_inv = np.linalg.inv(K)
M = np.dot(K_inv, H)

# [r_1, r_2, t] = M
r1 = M[:, 0] 
r2 = M[:, 1] 

#Calcular factor lambda para que r1 y r2 tengan norma unidad
r1_norma = np.linalg.norm(r1)
r2_norma = np.linalg.norm(r2)

# Lambda = 1/media de las normas
media = (r1_norma + r2_norma) / 2 # Calcular la media de las normas porque no son exactamente iguales
factorLambda = 1 / media

#Ahora tenemos que ver si el lambda será positivo o negativo.
# Para ello calcularemos r3 (r1 x r2), generaremos la matriz R y calcularemos det(R). 
# Si det(R)=1, habremos encontrado el signo de lambda.

#1. Proceso con lambda positivo
r1_pos = r1 * factorLambda
r2_pos = r2 * factorLambda
r3_pos = np.cross(r1_pos, r2_pos)

R_pos = np.column_stack((r1_pos, r2_pos, r3_pos))

print("Determinante de R con lambda positivo:", np.linalg.det(R_pos))
# Output: 0.9999987360478219

#2. Proceso con lambda negativo
r1_neg = r1 * -factorLambda
r2_neg = r2 * -factorLambda
r3_neg = - np.cross(r1_neg, r2_neg)

R_neg = np.column_stack((r1_neg, r2_neg, r3_neg))

print("Determinante de R con lambda negativo:", np.linalg.det(R_neg))
# Output: -0.9999987360478219

#Por tanto, lambda será positivo.

#Para que sea una matriz de rotación, tiene que ser ORTONORMAL: ortogonal + longitud 1 (determinante = 1 - ya comprobado)

# Ortogonal: R*R^T=1=I
R_inv = R_pos.T

#DESCOMENTAR para ver R^T R 
# np.set_printoptions(suppress=True, precision=4)
# print("R^T R = \n", R_pos @ R_inv)
# print("\n")

#El resultado de R^T*R no es una matriz de identidad, aunque los valores de la diagonal estén cerca de 1.
# Por tanto, no es una matriz de rotación válida

#Obtener t
t = M[:, 2] * factorLambda


#Guardar resultados
np.savetxt('resultados/parte3_1_R.txt', R_pos)
np.savetxt('resultados/parte3_1_t.txt', t)
    


############################################################################################
##################################### SEGUNDO EJERCICIO ####################################
############################################################################################

#Obtener las primeras 2 columnas de M
M_prima = M[:, :2]

#Aplicar SVD para obtener la descomposición
U_prima, S_prima, Vt_prima = np.linalg.svd(M_prima, full_matrices=False)

#R* = U Vt
R_star = np.dot(U_prima, Vt_prima)

#Calcular lambda
factorLambdaFinal = np.trace(np.dot(R_star.T, M_prima)) / np.trace(np.dot(M_prima.T, M_prima))

r3_star = np.cross(R_star[:, 0], R_star[:, 1])

R_final = np.column_stack((R_star, r3_star))

#det(R_final) = 1
det_final = np.linalg.det(R_final)
print("Determinante de la matriz R final", det_final)

# Ortogonal: R*R^T=1
R_final_inv = R_final.T

#DESCOMENTAR para ver R^T R 
# np.set_printoptions(suppress=True, precision=4)
# print("R^T R = \n", R_final @ R_final_inv)
# print("\n")


#Obtener t
t_final =  M[:, 2] * factorLambdaFinal


#Guardar resultados
np.savetxt('resultados/parte3_2_R.txt', R_final)
np.savetxt('resultados/parte3_2_t.txt', t_final)




############################################################################################
##################################### TERCER EJERCICIO #####################################
############################################################################################

frame = cv2.imread("./datos/imagenes/img_001.jpg") 
frame_copy = frame.copy()

# Dibujar ejes x, y, z
cv2.drawFrameAxes(frame_copy, K, 0, R_final, t_final, 8, 3)

cv2.imshow("Ajedrez con ejes X Y Z", frame_copy)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("resultados/parte3.png", frame_copy)


