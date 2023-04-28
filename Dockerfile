FROM python:3.9



WORKDIR /app
COPY ./requirements.txt /app/requirements.txt


RUN pip install -r  requirements.txt --use-deprecated=legacy-resolver

COPY ./app /app

# Run the run script, it will check for an /app/prestart.sh script (e.g. for migrations)
ENV PYTHONPATH=/app

