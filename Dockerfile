FROM python:3.13-slim

WORKDIR /opt/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY mk8dxlounge.py .

CMD ["python", "app.py"]