FROM python:3.12-slim

WORKDIR /app

RUN pip install fastapi==0.115.0
RUN pip install uvicorn[standard]==0.30.6
RUN pip install pydantic==2.9.2
RUN pip install python-dotenv==1.0.1

COPY . .

CMD ["python" "main.py"]