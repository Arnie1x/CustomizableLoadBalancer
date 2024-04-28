FROM python:3.10.12

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV SERVER_ID=1

CMD ["python", "server.py"]