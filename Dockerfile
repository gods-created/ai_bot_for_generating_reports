FROM python:3
COPY . /app
WORKDIR /app
RUN chmod -R 666 /app
RUN chmod +x /app/*
RUN pip install -r requirements.txt
CMD ["/app/entrypoint.sh"]