# Imagem base: Python oficial, versão "slim"
FROM python:3.13-slim

# Ferramentas de sistema (o git é usado pelo Dev Container e pra versionar)
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Usuário não-root com home próprio (necessário para o Dev Container)
# --shell /bin/bash: sem isso o padrão é /bin/sh (dash), um shell pobre
# sem histórico com setas nem autocomplete — o "terminal estranho".
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser

# Pasta de trabalho dentro do container
WORKDIR /code

# Copia SÓ o requirements primeiro
COPY requirements.txt .

# Instala as dependências dentro da imagem
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código pra dentro da imagem
COPY . .

# Deixa de rodar como root a partir daqui. O compose já fazia isso com `user:`,
# mas em produção não há compose nenhum pra corrigir a imagem.
USER appuser

# Documenta que a API usa a porta 8000
EXPOSE 8000

# Forma shell (sh -c) porque a forma exec não expande variável: o Cloud Run injeta
# a porta em $PORT, e o padrão 8000 mantém o comportamento local igual ao de antes.
CMD ["sh", "-c", "fastapi run app/main.py --host 0.0.0.0 --port ${PORT:-8000}"]
