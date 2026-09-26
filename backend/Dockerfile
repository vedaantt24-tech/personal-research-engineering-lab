FROM python:3.13-slim
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/data/media \
    && chown -R appuser:appuser /app
COPY --chown=appuser:appuser alembic.ini ./alembic.ini
COPY --chown=appuser:appuser backend/alembic ./backend/alembic
COPY --chown=appuser:appuser backend/app ./app
COPY --chown=appuser:appuser backend/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh
USER 10001:10001
EXPOSE 8000
CMD ["./entrypoint.sh"]
