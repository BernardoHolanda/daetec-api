# Imagem base: Python oficial, versão "slim"
FROM python:3.13-slim

# Ferramentas de sistema (o git é usado pelo Dev Container e pra versionar)
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Usuário não-root com home próprio (necessário para o Dev Container)
RUN useradd --create-home --uid 1000 appuser

# Pasta de trabalho dentro do container
WORKDIR /code

# Copia SÓ o requirements primeiro
COPY requirements.txt .

# Instala as dependências dentro da imagem
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código pra dentro da imagem
COPY . .

# Documenta que a API usa a porta 8000
EXPOSE 8000

# Comando que roda quando o container sobe
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]