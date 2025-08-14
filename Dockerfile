FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8000
CMD ["gunicorn", "-w", "1", "--threads", "4", "-b", "0.0.0.0:8000", "app.app:app"]

