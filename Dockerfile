FROM python:3.10-slim

# Actualizamos e instalamos las dependencias del sistema necesarias
# Se agregan gcc y build-essential para compilar extensiones en python-iptables
RUN apt-get update && apt-get install -y iptables libnetfilter-queue-dev gcc build-essential

WORKDIR /app

# Copiamos el archivo de requerimientos e instalamos las dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiamos el resto de la aplicación
COPY . .

# Ejecutamos la aplicación (en Docker el proceso se ejecuta como root)
CMD ["python", "main.py"]
