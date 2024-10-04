# Usa una imagen base con Python
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de tu proyecto al contenedor
COPY . .

# Instala las dependencias desde el archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE 8080

# Usa gunicorn para ejecutar la aplicación Flask en el puerto 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:app"]
