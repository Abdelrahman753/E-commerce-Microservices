FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y postgresql-client

COPY . .

CMD ["bash", "-c", "until pg_isready -h auth_db -p 5432; do sleep 1; done; python app.py"]
