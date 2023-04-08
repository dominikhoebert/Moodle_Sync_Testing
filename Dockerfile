FROM python:3.10
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY *.py ./

ENTRYPOINT ["python", "main.py"]
#docker run -it -v ${pwd}/data:/app/data moodle_sync_testing data/test.csv -i 1308 -c data/credentials.json -e email -g groupname -r
#https://stackoverflow.com/questions/41485217/mount-current-directory-as-a-volume-in-docker-on-windows-10
#delete container after use: --rm
#-it for interactive mode
#push!