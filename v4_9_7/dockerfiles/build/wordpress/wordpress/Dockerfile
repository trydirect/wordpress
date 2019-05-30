
# Set the base image to Ubuntu
FROM ubuntu:14.04

# File Author / Maintainer
MAINTAINER Lei SHI <foxshee@gmail.com>

# Default HTTP and HTTPS ports
EXPOSE 80 443


# Keep upstart from complaining
RUN dpkg-divert --local --rename --add /sbin/initctl && \
	ln -sf /bin/true /sbin/initctl

# Let the container know that there is no tty
ENV DEBIAN_FRONTEND noninteractive

# Update the repository sources list and finish upgrade
RUN apt-get update && apt-get -y upgrade
RUN groupadd -r -g 2000 wordpress; useradd -r -u 2000 -g 2000 -m -c "app account" -d /home/wordpress -s /bin/bash wordpress

#
RUN apt-get install -y mysql-client \
						php5-fpm \
						php5-mysql \
						pwgen \
						python-setuptools \
						curl \
						git \
						unzip

# **Wordpress** Dependencies
RUN apt-get install -y php5-curl \
						php5-gd \
						php5-intl \
						php-pear \
						php5-imagick \
						php5-imap \
						php5-mcrypt \
						php5-memcache \
						php5-ming \
						php5-ps \
						php5-pspell \
						php5-recode \
						php5-sqlite \
						php5-tidy \
						php5-xmlrpc \
						php5-xsl

### ---- FIX -----
# Fix 'add-apt-repository: not found' in Ubuntu 14.04 LTS
RUN apt-get -y install software-properties-common \
						python-software-properties



RUN add-apt-repository ppa:rtcamp/nginx && \
	apt-get update && \
	apt-get remove nginx* && \
	apt-get install -y nginx-custom


############################################################
# Configurations
#

# ----------------------------------------------------------
# Nginx Config
# ----------------------------------------------------------

# Copy config files to `/etc/nginx/` folder
COPY  config/nginx.conf /etc/nginx/nginx.conf

COPY  config/nginx-site-http.conf /etc/nginx/nginx-site-http.conf
COPY  config/nginx-site-https.conf /etc/nginx/nginx-site-https.conf
# Default **site** config - HTTP
# Later if need to enforce SSL, use `nginx-site-http.conf` instead.
RUN cp  /etc/nginx/nginx-site-https.conf /etc/nginx/sites-available/default

COPY  config/nginx-ssl.conf /etc/nginx/ssl-template.conf
COPY  config/nginx-restrictions.conf /etc/nginx/restrictions.conf


# ----------------------------------------------------------
# PHP-fpm Config
# ----------------------------------------------------------

RUN sed -i -e "s/;cgi.fix_pathinfo\s*=\s*1/cgi.fix_pathinfo = 0/g; s/expose_php\s*=\s*On/expose_php = Off/g" \
/etc/php5/fpm/php.ini
RUN sed -i -e "s/expose_php\s*=\s*On/expose_php = Off/g" /etc/php5/fpm/php.ini
RUN sed -i -e "s/upload_max_filesize\s*=\s*2M/upload_max_filesize = 100M/g; s/post_max_size\s*=\s*8M/post_max_size = 100M/g" \
/etc/php5/fpm/php.ini
#RUN sed -i -e "s/post_max_size\s*=\s*8M/post_max_size = 100M/g" /etc/php5/fpm/php.ini

RUN sed -i -e "s/;daemonize\s*=\s*yes/daemonize = no/g" /etc/php5/fpm/php-fpm.conf

COPY ./config/php/www.conf	/etc/php5/fpm/pool.d/www.conf

RUN sed -i -e"s/^;opcache.enable\s*=\s*0/opcache.enable = 1/; s/^;opcache.max_accelerated_files\s*=\s*2000/opcache.max_accelerated_files = 4000/" /etc/php5/fpm/php.ini


RUN /usr/bin/easy_install supervisor && \
	/usr/bin/easy_install supervisor-stdout
COPY  config/supervisord.conf /etc/supervisord.conf



# ===============================================================================
# Install Wordpress
#

# Get the code of  **latest** version.
RUN cd /usr/share/nginx/ && \
    curl -o wp-latest.tar.gz https://wordpress.org/wordpress-4.9.10.tar.gz && \
    tar -xvf wp-latest.tar.gz && \
    rm wp-latest.tar.gz

# Target **webroot** - `/usr/share/nginx/www`
RUN rm -rf /usr/share/nginx/www && \
	mv /usr/share/nginx/wordpress /usr/share/nginx/www && \
	chown -R www-data:www-data /usr/share/nginx/www



# ===============================================================================
# System Initialization
#

## Copy the **pre-defined** bash script
COPY bash/init.sh /init.sh
## Modify the permisison - make sure they are excuatable
RUN chmod 755 /init.sh

# Set up default CMD
CMD ["/bin/bash", "/init.sh"]

ADD ./scripts/letsencrypt-auto /opt/letsencrypt/letsencrypt-auto

RUN chmod +x /opt/letsencrypt/letsencrypt-auto; /opt/letsencrypt/letsencrypt-auto  --os-packages-only --install-only --non-interactive;


# ===============================================================================
# Volume Mounting
#
# - Wordpress webroot
# - Log
#

# Mount the volumes
VOLUME ["/usr/share/nginx/www", "/var/log"]
