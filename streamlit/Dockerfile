FROM python:3.9.13

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8500

CMD ["streamlit", "run", "main.py", "--server.port=8500"]