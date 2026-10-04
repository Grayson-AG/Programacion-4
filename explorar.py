# Script de exploracion. Tarea para el 22 de septiembre.
# Equipo: ____________________   Caso: ____________________
#
# COMO SE CORRE (con el entorno activado, se ve "(.venv)" al inicio de la linea):
#   Mac / Linux:   python3 explorar.py telco-churn.csv
#   Windows:       python explorar.py telco-churn.csv
# El nombre del archivo es el de SU caso, y el script y el CSV tienen que estar en la
# misma carpeta (o escriban la ruta completa al CSV).
#
# QUE SE ENTREGA: este archivo (.py) ya completo y una captura de la salida completa.
#
# COMO DEBE VERSE LA SALIDA (ejemplo con churn, recortado):
#   archivo         : telco-churn.csv
#   filas, columnas : (7043, 21)
#
#   1) Tipo de cada columna
#   customerID         object
#   SeniorCitizen       int64
#   MonthlyCharges    float64
#   TotalCharges       object      <- un numero que pandas leyo como texto: eso es un hallazgo
#   ...
#
#   2) Porcentaje de nulos por columna
#   customerID    0.0
#   ...
#
#   3) Las cinco columnas con mas valores unicos
#   customerID      7043           <- un identificador: no es una feature
#   TotalCharges    6531
#   MonthlyCharges  1585
#   tenure            73
#   PaymentMethod      4
#
#   4) Observaciones
#   a) ...
#   b) ...
#   c) ...

import sys
import pandas as pd

if len(sys.argv) < 2:
    print("Uso: python explorar.py su-archivo.csv")
    sys.exit(1)

ruta = sys.argv[1]
df = pd.read_csv(ruta)

print("archivo         :", ruta)
print("filas, columnas :", df.shape)

# 1) Tipo de cada columna.
#    Pista: df.dtypes
print("\n1) Tipo de cada columna")
# TODO: una linea


# 2) Porcentaje de nulos por columna.
#    Pista: df.isna().mean() da la proporcion (0 a 1); multipliquen por 100 y usen .round(2)
print("\n2) Porcentaje de nulos por columna")
# TODO: una linea


# 3) Las cinco columnas con mas valores unicos.
#    Pista: df.nunique().sort_values(ascending=False).head(5)
print("\n3) Las cinco columnas con mas valores unicos")
# TODO: una linea


# 4) Tres observaciones sobre SU dataset. Escribanlas como texto, una linea cada una.
#    a) La columna que mas les preocupa y por que (tipo raro, muchos nulos, rango imposible).
#    b) Una columna que NO debe entrar al modelo y por que (identificador, un solo valor, fuga de datos).
#    c) Que columna cambiaria primero si cambia el mundo de su caso.
observaciones = [
    "a) ",
    "b) ",
    "c) ",
]
print("\n4) Observaciones")
for o in observaciones:
    print(o)
