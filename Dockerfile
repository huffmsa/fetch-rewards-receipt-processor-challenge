FROM python:3.12

WORKDIR /var/app

COPY . .
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "api:api", "--host", "0.0.0.0"]
