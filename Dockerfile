FROM python:3.10-slim

WORKDIR /app

# Install System Dependencies for Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium

COPY . .

# Make script executable
RUN chmod +x start.sh

# Start
CMD ["./start.sh"]