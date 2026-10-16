#Titulo: Funciones asincronas
#Autor: Adrian Ramirez
#Fecha de creacion: 13/10/20206

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio

#Definimos la instancia principal del framework FastAPI donde se registrarán todas las rutas.
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#Generamos un arreglo con los productos de neustra tiendita
inventario = [
    {"id": 1, "nombre": "Whey protein 5lbs.", "precio": 1500, "cantidad": 1},
    {"id": 2, "nombre": "Barras de proteina", "precio": 25, "cantidad": 1},
    {"id": 3, "nombre": "Creatina monohidratada", "precio": 350, "cantidad": 1}
]

@app.get("/procesar")
async def procesar_pedido():
    # simulamos la consulta de una base de datos
    await asyncio.sleep(2)
    return {"mensaje": "Pedido procesado con exito"}

@app.get("/")
async def home():
    return {"Message": "Hola bienvenido"}

@app.get("/productos")
async def getProductos():
    return inventario

@app.post("/productos")
async def addProducto(producto: dict):
    nuevo_id = max((p["id"] for p in inventario), default=0) + 1
    producto["id"] = nuevo_id
    inventario.append(producto)
    return producto

@app.delete("/productos/{producto_id}")
async def deleteProducto(producto_id: int):
    for p in inventario:
        if p["id"] == producto_id:
            inventario.remove(p)
            return {"mensaje": "Producto eliminado"}
    raise HTTPException(status_code=404, detail="Producto no encontrado")