FROM python:3.14-slim

WORKDIR /app

COPY markitdown/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY markitdown/ /app/

ENTRYPOINT ["python", "/app/convert.py"]
