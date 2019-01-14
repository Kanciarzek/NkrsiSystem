FROM python:3.6

WORKDIR /usr/src/app
ENV SUPER_EMAIL=test@test.pl
ENV SUPER_PASSWORD=pass1234
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000 8080 4352

CMD bash -c "sleep 20; python ./manage.py makemigrations usersystem; python ./manage.py migrate; python ./manage.py initAdmin; python ./manage.py runserver 0.0.0.0:8000;"
