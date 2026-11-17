"""
Título: Proyecto Tiendita Gimnasio
Autor: Adrian ramirez
Fecha de creación: 07/10/2026
Descripción: Configuración de la API para gestión de inventario
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from pydantic import BaseModel, Field



app = FastAPI(title="API Proyecto Tiendita", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#Inicializamos variable lock (Condición de carrera)
lock = asyncio.Lock()


#Modelos de Pydantic
#Pedir al cliente que su petición debe estructurarse de esta manera.
class crearProducto(BaseModel):
    nombre: str = Field(..., min_length=1, description="Nombre del producto")
    precio: float = Field(..., gt=0, description="Precio del producto")
    cantidad: int = Field(..., ge=0, description="stock del producto")


#La salida de datos de la API debe de estructurarse de esta manera.
class respuestaProducto(BaseModel):
    id: int
    nombre: str
    precio: float
    cantidad: int


#Datos cargados (Simulación)
inventario = [
    {"id": 1, "nombre": "Whey Protein 5 lbs.", "precio": 1500, "cantidad": 45},
    {"id": 2, "nombre": "Barras de proteina", "precio": 25, "cantidad": 50},
    {"id": 3, "nombre": "Creatina monohidratada 300 gr.", "precio": 250, "cantidad": 100},
    {"id": 4, "nombre": "Creatina monohidratada citrus punch", "precio": 280, "cantidad": 90},
    {"id": 5, "nombre": "Whey Gold Protein 5 lbs.", "precio": 1600, "cantidad": 50},
    {"id": 6, "nombre": "ISO Ultra Pure protein 4.2 lbs.", "precio": 1400, "cantidad": 50},
    {"id": 7, "nombre": "L-Carnitina 500 ml.", "precio": 180, "cantidad": 60},
    {"id": 8, "nombre": "Combo mamado (1 Whey Protein, 1 Creatina monohidratada, 5 Barras de proteina.)", "precio": 1800, "cantidad": 40},
    {"id": 9, "nombre": "Pack Toallas de mano (3)", "precio": 80, "cantidad": 40},
    {"id": 10, "nombre": "Guantes acolchados", "precio": 60, "cantidad": 35}
]


#Prueba asyncio 5 segundos
@app.get("/prueba-asyncio")
async def pruebaAsyncio():
    try:
        print("empiezan los 5 segundos")
        await asyncio.sleep(5)
        print("Se acaba de terminar los 5 segundos")
        return {"Message": "Respuesta después de 5 segundos"}
    except Exception as error:
        print(f"Hubo un error: {error}")

#Prueba asyncio 3 segundos
@app.get("/prueba-asyncio-3segundos")
async def pruebaAsyncio():
    print("empiezan los 3 segundos")
    await asyncio.sleep(3)
    print("Se acaba de terminar los 3 segundos")
    return {"Message": "Respuesta después de 3 segundos"}

#Prueba asyncio 1 segundos
@app.get("/prueba-asyncio-1segundo")
async def pruebaAsyncio():
    print("empiezan los 1 segundos")
    await asyncio.sleep(1)
    print("Se acaba de terminar los 1 segundos")
    return {"Message": "Respuesta después de 1 segundos"}


#Ejemplo de API - GET para obtener mensaje inicial
@app.get("/")
def home():
    try:
        print("hola1") 
        resultado = "1"  +  1,
        print("hola2")
        return {"Message": "Hola bienvenido"}
    except Exception as error:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al hacer la operación: {str(error)}"
        )
       
   


#GET Obtiene lista de productos de mi inventario
@app.get("/productos")
def getProductos():
    try:
        return inventario
    except Exception as error:
        return  {str(error)} 

#POST Agrega producto a mi inventario
@app.post("/productos", response_model=respuestaProducto, status_code=status.HTTP_201_CREATED)
def addProducto(producto: crearProducto):
    try:

        nuevo_id = max((p["id"] for p in inventario), default=0) + 1
        nuevo_producto = {
            "id": nuevo_id,    
            "nombre": producto.nombre,
            "precio": producto.precio,
            "cantidad": producto.cantidad
        }

        inventario.append(nuevo_producto)

        return nuevo_producto
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al agregar el producto: {str(error)}"
        )

    
#DELETE Borra producto de mi inventario
@app.delete("/productos/{producto_id}")
def deleteProducto(producto_id: int):
    try:
        for producto in inventario:
            if producto["id"] == producto_id:
                inventario.remove(producto) #Elimina el producto del inventario ya que encontró el id correspondiente
                return {"Message": "El producto fue eliminado"}
        return {"Message": "No fue encontrado el producto"}
    except HTTPException as errorHTTP:
        return {str(errorHTTP)}

    except Exception as error:
        return  {str(error)} 


@app.post("/productos/{producto_id}")
async def comprarProducto(producto_id: int):
    try:
        async with lock:
            for objeto in inventario:
                if objeto["id"] == producto_id:
                    if objeto["cantidad"] > 0:
                        await asyncio.sleep(0.05)
                        objeto["cantidad"] = objeto["cantidad"]-1
                        return {"Mensaje":"Producto comprado"}
                    else:
                        raise HTTPException(
                            status_code = status.HTTP_400_BAD_REQUEST,
                            detail = "No hay stock de ese producto"
                        )

            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "No existe el ID de ese producto"
            )

    except Exception as error:
        raise HTTPException (
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Error al comprar producto: {str(error)}"
        )