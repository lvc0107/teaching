FROM python:3.12-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml pyproject.toml
COPY main.py main.py

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn[standard]

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
