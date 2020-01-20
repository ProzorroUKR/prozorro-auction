FROM python:3.7-slim
RUN mkdir /app
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git && apt-get purge -y --auto-remove && rm -rf /var/lib/apt/lists/*
ADD requirements.txt /app/
RUN pip install -r requirements.txt
COPY ./src /app
ENV API_OPT_FIELDS="status,procurementMethodType"
ENTRYPOINT ["python", "-m"]
CMD ["prozorro_auction.api.main"]