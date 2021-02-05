FROM python:3.7

RUN pip install Flask
RUN mkdir /app
WORKDIR /app
ADD /app/* /app/

EXPOSE 5000
#CMD ["python", "/app/main.py"]
CMD ["flask", "run", "--host", "0.0.0.0"]
