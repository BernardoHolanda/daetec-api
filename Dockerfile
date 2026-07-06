# 1. Imagem base: Python oficial, versão "slim"
FROM python:3.13-slim

# 2. Pasta de trabalho dentro do container
WORKDIR /code

# 3. Copia SÓ o requirements primeiro
COPY requirements.txt .

# 4. Instala as dependências dentro da imagem
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia o resto do código pra dentro da imagem
COPY . .

# 6. Documenta que a API usa a porta 8000
EXPOSE 8000

# 7. Comando que roda quando o container sobe
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]