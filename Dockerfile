FROM continuumio/anaconda3:latest
#define the working directory of Docker container
WORKDIR /app 

#copy everything in ./actions directory (your custom actions code) to /app/actions in container
COPY ./ ./

# install dependencies
#RUN pip install -r requirements.txt

#RUN mkdir output-small
RUN pip install gunicorn
RUN pip install deep-translator

RUN ls
# command to run on container start
#CMD [ "python", "./app.py" ]
CMD exec gunicorn --bind :$PORT --workers 1 --threads 1 --timeout 0 app:app

#EXPOSE 5005