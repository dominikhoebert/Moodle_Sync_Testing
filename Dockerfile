FROM python:3.10-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY *.py ./

ENTRYPOINT ["python", "main.py"]
