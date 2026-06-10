FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p output/history credentials

EXPOSE 8080

ENV PORT=8080

CMD streamlit run src/app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
