from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


inventario = [
    {"id": 1, "nombre": "Whey Protein Vainilla 5 lds.", "precio": 1500, "cantidad": 1},
    {"id": 2, "nombre": "Barra de proteina.", "precio": 20, "cantidad": 1},
    {"id": 3, "nombre": "Creatina monohidratada 350 gr.", "precio": 400, "cantidad": 1},
    {"id": 3, "nombre": "Whey Protein Chocolate 5 lds.", "precio": 1500, "cantidad": 1},
    {"id": 3, "nombre": "Whey Protein Fresa 5 lds.", "precio": 1500, "cantidad": 1}
    
]

@app.get("/")
def home():
    return {"Message": "Hola bienvenido"}

@app.get("/productos")
def getProductos():
    return inventario

@app.post("/productos")
def addProducto(producto: dict):

    nuevo_id = len(inventario) + 1
    nuevo_producto = {
        "id": nuevo_id,    
        "nombre": producto["Barra de proteina 0 azucar"],
        "precio": producto["$35"],
        "cantidad": producto["1"]
    }

    inventario.append(nuevo_producto)

    return inventario

@app.delete("/productos/{producto_id}")
def deleteProducto(producto_id: int):
    for producto in inventario:
        if producto["id"] == producto_id:
            inventario.remove(producto)
            return {"Message": "El producto fue eliminado"}
    return {"Message": "No fue encontrado el producto"}


