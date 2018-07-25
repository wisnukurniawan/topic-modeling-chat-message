FROM python:3.6-slim

# app workdir
WORKDIR /app

# copy app dependencies
COPY requirements.txt ./

# install dependecies
RUN apk add --update bash musl-dev build-base gcc libffi-dev make \
    # install dependencies
    && pip install -r ./requirements.txt \
    # clean pip cache
    && rm -rf /root/.cache/pip/* \
    # clean system dependencies
    && rm -rf /var/cache/apk/*

# build app source code
COPY . ./

# Default runtime configs
EXPOSE 8080
CMD ["python", "app.py"]