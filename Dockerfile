FROM python:3-slim

COPY . /ci

WORKDIR /ci

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3", "main.py"]