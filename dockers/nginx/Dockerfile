FROM faizanbashir/alpine:latest
LABEL MAINTAINER="Faizan Bashir <faizan.ibn.bashir@gmail.com>"

RUN apk --update add nginx && \
    ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log && \
    mkdir /etc/nginx/sites-enabled/ && \
    mkdir -p /etc/letsencrypt/webrootauth && \
    mkdir -p /run/nginx && \
    rm -rf /var/www/* && \
    rm -rf /etc/nginx/conf.d/default.conf && \
    touch /var/www/favicon.ico && \
    rm -rf /var/cache/apk/*

COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/app.conf /etc/nginx/conf.d/app.conf

#COPY nginx-selfsigned.key /etc/ssl/private/nginx-selfsigned.key
#COPY nginx-selfsigned.crt /etc/ssl/certs/nginx-selfsigned.crt

# RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt

# EXPOSE 80 443
# CMD ["nginx", "-g", "daemon off;"]
