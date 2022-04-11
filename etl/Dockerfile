FROM python:3.8-slim-buster
COPY . /root
WORKDIR /root/
RUN apt-get update && apt-get -y install cron
RUN pip install -r requirements.txt
RUN chmod 0644 crontab
RUN crontab crontab
RUN touch /var/log/cron.log
CMD cron && tail -f /var/log/cron.log
