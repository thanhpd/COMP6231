# Use an official NGINX image as the base
FROM nginx:latest

# Copy custom NGINX config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy static frontend files to the NGINX default directory
COPY . /usr/share/nginx/html

# Expose port 80 for the web server
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
