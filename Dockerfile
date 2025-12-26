FROM python:3.11-slim
WORKDIR /app
COPY api/ .
RUN pip install --no-cache-dir flask bcrypt
USER nobody
EXPOSE 5000
CMD ["python", "app.py"]
