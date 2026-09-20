FROM docker.m.daocloud.io/library/python:3.12
WORKDIR /app
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
