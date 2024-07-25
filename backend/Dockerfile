FROM python:3.9
# Base docker image of python 3.x

RUN apt-get -y update; apt-get -y upgrade; apt-get -y install curl 
# Update the apt-get package and install curl for healthcheck

RUN pip install --upgrade pip
# Upgrade pip package

WORKDIR /app
# Change working dir to app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt
# Copy main.py and requirements.txt from local into app dir inside the container

# RUN pip install -r requirements.txt
# Refering to copied file inside the app dir install the user dependency

COPY . /app

EXPOSE 8000
# Expose a port inside the container on which services run

CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "220"]
# gunicorn command to run the service with 4 worker nodes binding localhost/0.0.0.0 on port 8095 refering app inside the main.py