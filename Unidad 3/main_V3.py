"""
Título: Proyecto Tiendita Gimnasio
Autor: Adrian Ramirez
Fecha de creación: 07/10/2026
Descripción: Configuración de la API para gestión de inventario
"""

import os
import csv
import asyncio
from datetime import datetime
from typing import List
from collections import deque

import pandas as pd
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# --- Configuración Inicial ---
app = FastAPI(title="API Tiendita", version="2.0")

# Habilitar CORS para permitir conexiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar el dominio exacto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Control de Tráfico (Rate Limiting Simple) ---
# Almacén temporal de marcas de tiempo
historial_peticiones = []
LIMITE_PETICIONES = 1000
VENTANA_TIEMPO = 1.0  # segundos

@app.middleware("http")
async def limitar_trafico(request: Request, call_next):
    """Middleware básico para prevenir abuso de la API."""
    ahora = asyncio.get_event_loop().time()
    
    # Filtrar peticiones antiguas fuera de la ventana de tiempo
    global historial_peticiones
    historial_peticiones = [t for t in historial_peticiones if t > ahora - VENTANA_TIEMPO]

    if len(historial_peticiones) >= LIMITE_PETICIONES:
        return JSONResponse(
            status_code=429,
            content={"error": "Límite excedido", "detail": "Demasiadas solicitudes rápidas. Espere un momento."}
        )

    historial_peticiones.append(ahora)
    respuesta = await call_next(request)
    return respuesta

# --- Modelos de Datos (Pydantic) ---

class EsquemaEntrada(BaseModel):
    """Validación para crear un nuevo producto."""
    nombre: str = Field(..., min_length=1, description="Nombre del artículo")
    precio: float = Field(..., gt=0, description="Costo unitario")
    cantidad: int = Field(..., ge=0, description="Stock inicial")

class EsquemaSalida(BaseModel):
    """Estructura de respuesta para productos."""
    id: int
    nombre: str
    precio: float
    cantidad: int

class RespuestaTransaccion(BaseModel):
    mensaje: str

# --- Utilidades de Persistencia (CSV) ---

RUTA_INVENTARIO = "productos.csv"
RUTA_VENTAS = "ventas.csv"

def leer_inventario():
    """Lee el archivo CSV y retorna una lista de diccionarios."""
    if not os.path.exists(RUTA_INVENTARIO):
        return []
    
    lista_productos = []
    with open(RUTA_INVENTARIO, mode="r", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            # Convertir tipos de datos explícitamente
            lista_productos.append({
                "id": int(fila["id"]),
                "nombre": fila["nombre"],
                "precio": float(fila["precio"]),
                "cantidad": int(fila["cantidad"])
            })
    return lista_productos

def escribir_inventario(datos):
    """Sobrescribe el CSV con los datos actuales del inventario."""
    campos = ["id", "nombre", "precio", "cantidad"]
    with open(RUTA_INVENTARIO, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(datos)

def registrar_transaccion(nombre_prod, precio_unitario, qty=1):
    """Añade una línea al registro histórico de ventas."""
    existe_archivo = os.path.isfile(RUTA_VENTAS)
    
    with open(RUTA_VENTAS, mode="a", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        
        # Si es la primera vez, escribir cabeceras
        if not existe_archivo:
            escritor.writerow(["id_venta", "fecha_hora", "producto", "precio_u", "cantidad", "total"])
            siguiente_id = 1
        else:
            # Contar líneas para generar ID autoincremental simple
            with open(RUTA_VENTAS, "r", encoding="utf-8") as f:
                siguiente_id = sum(1 for _ in f)
        
        total_pago = precio_unitario * qty
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        escritor.writerow([siguiente_id, fecha_actual, nombre_prod.strip(), precio_unitario, qty, total_pago])

# --- Endpoints Principales ---

@app.get("/")
def raiz():
    return {"status": "online", "servicio": "Tiendita API v2"}

@app.get("/productos", response_model=List[EsquemaSalida])
def listar_articulos():
    try:
        return leer_inventario()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo al leer datos: {str(e)}")

@app.post("/productos", response_model=EsquemaSalida, status_code=status.HTTP_201_CREATED)
def agregar_articulo(nuevo_item: EsquemaEntrada):
    try:
        inventario_actual = leer_inventario()
        
        # Calcular nuevo ID
        ids_existentes = [p["id"] for p in inventario_actual]
        nuevo_id = max(ids_existentes) + 1 if ids_existentes else 1
        
        producto_dict = {
            "id": nuevo_id,
            "nombre": nuevo_item.nombre,
            "precio": nuevo_item.precio,
            "cantidad": nuevo_item.cantidad
        }
        
        inventario_actual.append(producto_dict)
        escribir_inventario(inventario_actual)
        
        return producto_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar: {str(e)}")

@app.delete("/productos/{item_id}")
def borrar_articulo(item_id: int):
    inventario = leer_inventario()
    
    # Buscar el índice del producto a eliminar
    producto_a_borrar = next((p for p in inventario if p["id"] == item_id), None)
    
    if not producto_a_borrar:
        raise HTTPException(status_code=404, detail="ID no encontrado en el inventario")
    
    inventario.remove(producto_a_borrar)
    escribir_inventario(inventario)
    
    return {"mensaje": "Artículo eliminado correctamente"}

# Lock para evitar condiciones de carrera en compras simultáneas
candado_compra = asyncio.Lock()

@app.post("/productos/{item_id}", response_model=RespuestaTransaccion)
async def procesar_compra(item_id: int):
    async with candado_compra:
        inventario = leer_inventario()
        
        # Buscar producto eficientemente
        producto_obj = next((p for p in inventario if p["id"] == item_id), None)
        
        if not producto_obj:
            raise HTTPException(status_code=404, detail="El producto solicitado no existe")
        
        if producto_obj["cantidad"] <= 0:
            raise HTTPException(status_code=400, detail="Agotado: No hay unidades disponibles")
        
        # Simular procesamiento y actualizar stock
        await asyncio.sleep(0.05) 
        producto_obj["cantidad"] -= 1
        
        # Guardar estado actualizado
        escribir_inventario(inventario)
        
        # Registrar venta externamente al lock para ser más rápido
        registrar_transaccion(
            nombre_prod=producto_obj["nombre"],
            precio_unitario=producto_obj["precio"]
        )
        
        return RespuestaTransaccion(mensaje="Compra exitosa")

# --- Endpoints de Analítica ---

@app.get("/api/analisis/mas-vendidos")
def ranking_ventas():
    if not os.path.exists(RUTA_VENTAS):
        return []
    
    df = pd.read_csv(RUTA_VENTAS)
    if df.empty:
        return []
    
    # Agrupar por producto y sumar montos
    resumen = df.groupby("producto")["total"].sum().reset_index()
    resumen.columns = ["producto", "monto_total"] # Asegurar nombres de columna consistentes con el frontend
    
    # Ordenar descendente
    resumen = resumen.sort_values(by="monto_total", ascending=False)
    
    return resumen.to_dict(orient="records")

@app.get("/api/analisis/kpis")
def dashboard_kpis():
    if not os.path.exists(RUTA_VENTAS):
        return {"ingresos_totales": 0, "producto_estrella": "N/A", "ticket_promedio": 0}
    
    df = pd.read_csv(RUTA_VENTAS)
    if df.empty:
        return {"ingresos_totales": 0, "producto_estrella": "N/A", "ticket_promedio": 0}
    
    total_ingresos = float(df["total"].sum())
    promedio_ticket = float(df["total"].mean())
    
    # Producto más rentable
    top_producto_df = df.groupby("producto")["total"].sum().idxmax()
    nombre_estrella = df.loc[df.groupby("producto")["total"].sum().idxmax(), "producto"] if not df.empty else "N/A"
    
    # Recalcular nombre estrella de forma segura
    agrupado = df.groupby("producto")["total"].sum()
    if not agrupado.empty:
        nombre_estrella = agrupado.idxmax()
    else:
        nombre_estrella = "N/A"

    return {
        "ingresos_totales": round(total_ingresos, 2),
        "producto_estrella": nombre_estrella,
        "ticket_promedio": round(promedio_ticket, 2)
    }