# 1. Use Python 3.10
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies required for Chrome/Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy the requirements file
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Install Playwright Browsers (Crucial for your scanner)
# We install Chromium and its system dependencies
RUN playwright install --with-deps chromium

# 7. Copy the rest of your application code
COPY . .

# 8. Copy the start script and make it executable
COPY start.sh .
RUN chmod +x start.sh

# 9. Expose the port (Hugging Face uses 7860)
EXPOSE 7860

# 10. Run the start script
CMD ["./start.sh"]