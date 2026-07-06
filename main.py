from fastapi import FastAPI

app = FastAPI(title="DAETEC API")

@app.get("/")
def raiz():
    return {"mensagem": "Olá mundo — agora com hot reload!"}