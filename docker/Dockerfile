FROM python:3.6

# app workdir
WORKDIR /app

# copy app dependencies
COPY ../requirements.txt ./

# install dependecies
RUN apt-get update
RUN apt-get install -y bash musl-dev gcc libffi-dev make git libblas-dev liblapack-dev gfortran \
    # install app dependencies
    && pip install -r ./requirements.txt --upgrade \
    # clean pip cache
    && rm -rf /root/.cache/pip/*

# build app source code
COPY . ./

# Default runtime configs
EXPOSE 8080
CMD ["python", "./app.py"]