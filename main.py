from fast api import FastAPI

app = FastAPI(title="DAETEC API")

@app.get("/")
    def raiz():
        return {"mensagem": "Olá mundo - DAETEC API no ar!"}