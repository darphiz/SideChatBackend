FROM python:3.11.5
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt
# Create app log directory
RUN mkdir -p /var/log/app
# create app log file
RUN touch /var/log/app/app.log

COPY . /app/
EXPOSE 8080
ENTRYPOINT [ "/bin/bash" ]
CMD ["startserver.sh"]