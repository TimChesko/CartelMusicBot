FROM python:3.11

WORKDIR /app

COPY ./src /app/src
COPY pyproject.toml poetry.lock /app/

RUN pip3 install poetry==1.5.1 \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

CMD ["poetry", "run", "cartel_bot"]
