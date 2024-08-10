# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    xvfb \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y \
    google-chrome-stable \
    fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its dependencies
RUN playwright install chromium
RUN playwright install-deps

# Copy your Python script into the container
COPY tiktok_scraper.py .
COPY helper.py .

# Create a script to run Xvfb and your Python script
RUN echo '#!/bin/bash\nXvfb :99 -ac &\nexport DISPLAY=:99\npython tiktok_scraper.py' > run.sh
RUN chmod +x run.sh

# Run the script when the container launches
CMD ["./run.sh"]