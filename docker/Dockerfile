FROM python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6

WORKDIR /app

COPY markitdown/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY markitdown/ /app/

ENTRYPOINT ["python", "/app/convert.py"]
