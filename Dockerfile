FROM python:3.9-slim-bullseye

WORKDIR /app

COPY transactions.py .

RUN pip install requests beautifulsoup4 pandas

CMD ["python", "transactions.py"]