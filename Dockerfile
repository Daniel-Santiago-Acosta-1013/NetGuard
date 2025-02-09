FROM python:3.10-slim

# Actualizamos e instalamos las dependencias del sistema necesarias
# Se agregan gcc, build-essential y wireless-tools (para iwgetid)
RUN apt-get update && apt-get install -y \
    iptables \
    libnetfilter-queue-dev \
    gcc \
    build-essential \
    wireless-tools

WORKDIR /app

# Copiamos el archivo de requerimientos e instalamos las dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiamos el resto de la aplicación
COPY . .

# Ejecutamos la aplicación (en Docker el proceso se ejecuta como root)
CMD ["python", "main.py"]
