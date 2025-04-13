# Use a base image, since our app is python based hence a python base image suits well.
FROM python:3.9.22-alpine3.21

#Set Work directory
WORKDIR /app

# Copy all files from current directory to /app
COPY . /app

# install the dependencies.
RUN python -m pip install --no-cache-dir -r requirements.txt

# Start app, setting ubuffered to capture all the console logs
CMD ["python","-u","app.py"]
