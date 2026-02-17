FROM python:3.9-slim
WORKDIR /app
RUN pip install flask authlib requests
COPY testapp.py .
CMD ["python", "testapp.py"]