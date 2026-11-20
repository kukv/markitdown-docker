FROM python:3.14-slim@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f

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
