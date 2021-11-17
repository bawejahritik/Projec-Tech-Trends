FROM python:2.7
COPY ./techtrends /app
WORKDIR /app
RUN python -m pip install --upgrade pip && pip install -r requirements.txt && python init_db.py
EXPOSE 3111
CMD [ "python", "app.py" ]