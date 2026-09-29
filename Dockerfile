FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies first so this layer is cached until the lockfile changes.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev

RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8501

# ddtrace-run enables APM and the AI Guard LangChain integration without code changes.
CMD ["uv", "run", "--no-sync", "ddtrace-run", "streamlit", "run", "src/wtpdf/app.py", \
     "--server.address=0.0.0.0", "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
