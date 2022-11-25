FROM nginx:stable

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

RUN apt-get update && apt-get install -y -q certbot python3-certbot-nginx
