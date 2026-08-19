FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV WDM_LOG_LEVEL=0

# Install dependencies for Chrome/Selenium
RUN apk update && apk add --no-cache \
    chromium \
    chromium-chromedriver \
    bash \
    build-base \
    libffi-dev

# Set the Chrome driver and binary path environment variables
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROME_DRIVER=/usr/bin/chromedriver

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Run the bot
CMD ["python", "src/main.py"]
