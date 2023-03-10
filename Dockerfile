FROM python:3.8-alpine
EXPOSE 9688

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./xui-exporter /app
WORKDIR /app

USER nobody
ENTRYPOINT ["python"]
CMD ["main.py"]