FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Install Nginx
RUN apt-get update && apt-get install -y nginx

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Copy the application files
COPY . /app

# Set the working directory
WORKDIR /app

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Nginx will run on
EXPOSE 80

# Run the Nginx server and Gunicorn
CMD ["sh", "-c", "nginx && gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app"]