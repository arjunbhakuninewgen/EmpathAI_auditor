# 1. Use the Official Playwright Image (Includes Python + Browsers + OS Deps)
# This skips the slow 'apt-get' and 'playwright install' steps!
FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

WORKDIR /app

# 2. Copy Requirements
COPY requirements.txt .

# 3. Install Python Libraries
# We use --no-deps for playwright to avoid re-downloading the binary if possible
RUN pip install -r requirements.txt

# 4. Copy Application Code
COPY . .

# 5. Permissions
RUN chmod +x start.sh

# 6. Start
CMD ["./start.sh"]