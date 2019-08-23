FROM python:2

WORKDIR /usr/src/app

COPY ./scripts/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./scripts/ .

CMD [ "python", "./ScanProject.py" ]
