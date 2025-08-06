FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y postgresql-client

COPY . .

CMD ["bash", "-c", "until pg_isready -h product_db -p 5432; do sleep 1; done; python product.py"]
