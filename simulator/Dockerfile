FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY simulator.py telemetry.py ./

RUN useradd --create-home simulator
USER simulator

ENTRYPOINT ["python", "simulator.py"]
