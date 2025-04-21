# ============================
# СТАДИЯ 1 — Сборка
# ============================
FROM python:3.11-alpine AS builder

RUN apk add --no-cache build-base

WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

# ============================
# СТАДИЯ 2 — Финальный образ
# ============================
FROM python:3.11-alpine

RUN adduser -D appuser

COPY --from=builder /install /usr/local

WORKDIR /app
COPY . .

USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]
