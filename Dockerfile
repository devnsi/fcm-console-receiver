# --- Builder ---
FROM ghcr.io/astral-sh/uv:debian AS builder
WORKDIR /build

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY src/ ./src/
RUN uv run pyinstaller --onefile \
      --name "fcm-console-receiver" \
      --noconfirm \
      --specpath ./build \
      src/fcm_console_receiver/show_notifications.py

# --- Runtime ---
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder --chmod=755 /build/dist/fcm-console-receiver ./fcm-console-receiver

ENTRYPOINT ["./fcm-console-receiver"]
