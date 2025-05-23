# heatmapp_tcc/Dockerfile
# Este Dockerfile prepara o ambiente Python para o projeto de heatmap.

# Usa uma imagem oficial Python leve
FROM python:3.10-slim-buster

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências Python.
# O "--no-cache-dir" evita a criação de cache de pacotes para manter a imagem menor.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto Python para o container.
# Isso inclui main.py e a estrutura de pastas inicial.
COPY . .

# Nenhuma alteração no CMD, pois este container será iniciado sem executar
# automaticamente o script Python. Você o executará manualmente via `docker exec`.