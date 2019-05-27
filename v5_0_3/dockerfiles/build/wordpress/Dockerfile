FROM ubuntu:16.04

LABEL maintainer="info@optimum-web.com"


# no tty for container
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y software-properties-common \
                      mysql-client php-fpm php-mysql python-setuptools curl git unzip \
                      php-dev libmcrypt-dev gcc make autoconf libc-dev pkg-config \
                      php-curl php-gd php-intl php-pear php-imagick php-imap php-memcache \
					  php-pspell php-recode php-mcrypt php-tidy php-xmlrpc php-xsl supervisor

RUN groupadd -r -g 2000 wordpress; useradd -r -u 2000 -g 2000 -m -c "app account" -d /home/wordpress -s /bin/bash wordpress

WORKDIR /var/www/html
# Install Wordpress
RUN curl -LO https://github.com/WordPress/WordPress/archive/5.0.3.tar.gz && \
    tar -xf 5.0.3.tar.gz && rm 5.0.3.tar.gz

#RUN rm -rf /usr/share/nginx/www && mv /usr/share/nginx/wordpress /usr/share/nginx/www && \
#	chown -R www-data:www-data /usr/share/nginx/www
RUN mkdir -p /usr/share/nginx
RUN ln -s /var/www/html/WordPress-5.0.3 /usr/share/nginx/www

RUN mkdir /run/php

RUN chown -R wordpress. /run/php && \
    chown -R wordpress. /var/log/supervisor

# Copy wp-config
COPY config/www.conf /etc/php/7.0/fpm/pool.d
COPY config/wp-config.php /usr/share/nginx/www/wp-config.php
COPY config/supervisord.conf /etc/supervisord.conf
COPY config/php-fpm.conf /etc/php/7.0/fpm/php-fpm.conf

# ----------------------------------------------------------
# PHP-fpm Configgi
# ----------------------------------------------------------
RUN sed -i -e "s/;cgi.fix_pathinfo\s*=\s*1/cgi.fix_pathinfo = 0/g; s/expose_php\s*=\s*On/expose_php = Off/g" \
/etc/php/7.0/fpm/php.ini
RUN sed -i -e "s/expose_php\s*=\s*On/expose_php = Off/g" /etc/php/7.0/fpm/php.ini
RUN sed -i -e "s/upload_max_filesize\s*=\s*2M/upload_max_filesize = 100M/g; s/post_max_size\s*=\s*8M/post_max_size = 100M/g" \
/etc/php/7.0/fpm/php.ini
RUN sed -i -e "s/;daemonize\s*=\s*yes/daemonize = no/g" /etc/php/7.0/fpm/php-fpm.conf
RUN sed -i -e"s/^;opcache.enable\s*=\s*0/opcache.enable = 1/; s/^;opcache.max_accelerated_files\s*=\s*2000/opcache.max_accelerated_files = 4000/" /etc/php/7.0/fpm/php.ini

VOLUME ["/var/www/html", "/var/log"]
EXPOSE 9000
