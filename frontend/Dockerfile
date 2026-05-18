FROM nginx:alpine

# Copy frontend assets to nginx static directory
COPY . /usr/share/nginx/html

# Custom nginx config to handle SPA routing if needed (optional but good practice)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
