# ============================
# СТАДИЯ 1 — Сборка
# ============================
FROM python:3.11-alpine AS builder
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /usr/src/app

RUN pip install --upgrade pip

RUN apk update \
    && apk add gcc python3-dev
# Устанавливает остальные зависимости
COPY ./src/requirements.txt ./
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# ============================
# СТАДИЯ 2 — Финальный образ
# ============================
FROM python:3.11-alpine

RUN apk update

RUN adduser -D appuser

ENV APP_HOME=/app

RUN mkdir $APP_HOME
WORKDIR $APP_HOME


RUN chown -R appuser:appuser $APP_HOME


COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install \
      --no-cache-dir \
      --no-index \
      --find-links=/wheels \
      -r requirements.txt

python -m grpc_tools.protoc -I lab3 --python_out=./lab3 --grpc_python_out=./lab3 citygame.proto

COPY ./src .
RUN chown -R appuser:appuser $APP_HOME
RUN chmod +x $APP_HOME/entrypoint.sh
USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]
