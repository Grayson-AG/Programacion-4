from fastapi import FastAPI 
import time 

app = FastAPI()

@app.middleware("http")
async def medir_tiempo(request, call_next):
    inicio = time.time()
    response = await call_next (request)
    fin = time.time ()
    process_time = time - inicio
    response.headers = ["X-Process-Time"] = str (process_time)
    return response

@app.get("/")
def inicio():
    return {"mensaje" : "Hola mundo"}

@app.get("/usuarios")
def usuarios():
    return [
        {id : 1, "nombre" : "Diego"}
        {id : 2, "nombre" : "Ana"}
    ]