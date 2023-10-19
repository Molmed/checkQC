# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt and deploy app
RUN pip install --trusted-host pypi.python.org -r requirements/dev && \
    python setup.py develop

# Make port 80 available to the world outside this container
EXPOSE 80

# Start the web service when the container launches
ENTRYPOINT ["checkqc-ws", "--port=80", "--debug"]
CMD ["/app/tests/resources"]
