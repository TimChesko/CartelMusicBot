FROM python:3.10
WORKDIR /app
COPY src /app/src
COPY poetry.lock pyproject.toml /app/
RUN pip3 install --upgrade setuptools \
    && pip3 install poetry==1.5.1 \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi \
    && chmod 755 .
COPY . .