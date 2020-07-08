FROM nginx:stable

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

RUN apt-get update && apt-get install certbot python-certbot-nginx && certbot --nginx --non-interactive --agree-tos --email drakeapp@gmail.com -d tanukai.com
