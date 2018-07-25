FROM python:3.6-slim

# app workdir
WORKDIR /app

# copy app dependencies
COPY requirements.txt ./

# install dependecies
RUN pip install -r ./requirements.txt

# build app source code
COPY . ./

# Default runtime configs
EXPOSE 8080
CMD ["python", "app.py"]