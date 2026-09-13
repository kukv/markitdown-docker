FROM python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6

# uid/gid 1000 matches the default first user on most Linux desktops, so a bind-mounted
# data/output is writable without extra setup. The base image leaves 1000 unused.
RUN groupadd -g 1000 markitdown \
    && useradd -u 1000 -g markitdown -m -s /usr/sbin/nologin markitdown \
    && mkdir -p /data/input /data/output \
    && chown -R markitdown:markitdown /data

WORKDIR /app

COPY markitdown/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY markitdown/ /app/

USER markitdown

ENTRYPOINT ["python", "/app/convert.py"]
