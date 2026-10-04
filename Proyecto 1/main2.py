# Importamos las librerías necesarias para crear la API REST con FastAPI y manejar los datos de las tareas.
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
# Creamos la instancia principal del framework FastAPI donde se registrarán todas las rutas.
app = FastAPI()

# Definimos una clase para validar los datos necesarios al crear o actualizar una tarea (hereda de BaseModel).
class Tarea(BaseModel):
    id: int  
    titulo: str  
    descripcion: Optional[str] = None  # Descripción detallada opcional (por defecto es None).
    completada: bool = False  
    
# Definimos una clase con campos opcionales para permitir actualizaciones parciales (PATCH/PUT) de una tarea.
class TareaUpdate(BaseModel):
    titulo: Optional[str] = None  # Nuevo título si se desea cambiar.
    descripcion: Optional[str] = None  # Nueva descripción si se desea cambiar.
    completada: Optional[bool] = None  # Nuevo estado de finalización si se desea actualizar.


db_tareas = []


# --- DeCORADOR Y RUTA: CREATE (Crear una tarea) ---
@app.post("/tareas/", status_code=201)
def crear_tarea(tarea: Tarea):
    for t in db_tareas:
        if t.id == tarea.id:
            # Si el id ya existe, lanzamos un error 400 Bad Request deteniendo la ejecución.
            raise HTTPException(status_code=400, detail="El ID de la tarea ya existe.")
    
    db_tareas.append(tarea.dict())
    
    return tarea


# --- DECORADOR Y RUTA: READ ALL (Obtener todas las tareas) ---
@app.get("/tareas/")
def obtener_tareas():
    
    return db_tareas


# --- DECORADOR Y RUTA: READ ONE (Obtener una tarea específica por ID) ---
@app.get("/tareas/{tarea_id}")
def obtener_tarea_por_id(tarea_id: int):
    for tarea in db_tareas:
        if tarea["id"] == tarea_id:
            return tarea
    raise HTTPException(status_code=404, detail="Tarea no encontrada.")


# --- DECORADOR Y RUTA: UPDATE (Actualizar una tarea existente) ---
@app.put("/tareas/{tarea_id}")
def actualizar_tarea(tarea_id: int, datos_actualizados: TareaUpdate):
    for index, tarea in enumerate(db_tareas):
        if tarea["id"] == tarea_id:
            update_data = datos_actualizados.dict(exclude_unset=True)
            tarea.update(update_data)            
            db_tareas[index] = tarea
            
            return {"mensaje": "Tarea actualizada con éxito", "tarea": tarea}
            
    # Si el ID no existe en la lista, lanzamos un error 404 Not Found.
    raise HTTPException(status_code=404, detail="Tarea no encontrada.")


# --- DECORADOR Y RUTA: DELETE (Eliminar una tarea por ID) ---
@app.delete("/tareas/{tarea_id}")
def eliminar_tarea(tarea_id: int):
    for index, tarea in enumerate(db_tareas):
        if tarea["id"] == tarea_id:
            db_tareas.pop(index)
            
            return {"mensaje": f"La tarea con ID {tarea_id} fue eliminada con éxito."}
            
    raise HTTPException(status_code=404, detail="Tarea no encontrada.")