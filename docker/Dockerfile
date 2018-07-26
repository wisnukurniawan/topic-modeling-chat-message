FROM python:3.6-alpine

# app workdir
WORKDIR /app

# copy app dependencies
COPY requirements.txt docker/*.sh ./

# install dependecies
RUN apk add --update bash musl-dev build-base gcc libffi-dev make git \
    # install app dependencies
    && pip install -r ./requirements.txt --upgrade \
    # clean pip cache
    && rm -rf /root/.cache/pip/* \
    # clean system dependencies
    && rm -rf /var/cache/apk/*

# build app source code
COPY . ./

# Default runtime configs
EXPOSE 8080
# CMD ["./wait-for-it.sh", "mysql:3306", "--", "python", "app.py"]
ENTRYPOINT ["./start.sh"]
CMD ["run"]