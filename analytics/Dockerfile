FROM python:3.12

WORKDIR /app
COPY pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/pip pip install .

WORKDIR /app/src
COPY src .

CMD [ "python", "main.py" ]