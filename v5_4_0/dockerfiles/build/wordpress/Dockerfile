ARG WP_VERSION=5.4.0-fpm

FROM wordpress:$WP_VERSION AS base

SHELL ["/bin/bash", "-c"]

RUN ls -la /usr/src/wordpress
RUN ls -la /var/www/html
RUN apt-get update -qq && apt-get install -qq -y --no-install-recommends --no-install-suggests \
        cron \
        supervisor \
    && mv /usr/src/wordpress/* /var/www/html \
    # clean up
    && find /usr/share/doc -depth -type f ! -name copyright|xargs rm || true \
    && find /usr/share/doc -empty|xargs rmdir || true \
    && rm -rf \
        /etc/supervisor/conf.d \
        /tmp/* \
        /usr/local/bin/docker-entrypoint.sh \
        /usr/share/{lintian,info}/* \
        /usr/src/* \
        /var/cache/man/* \
        /var/lib/apt/lists/* \
    # smoke tests
    && supervisord --version

COPY ./config/php.ini /usr/local/etc/php/conf.d/10-base.ini

WORKDIR /usr/src/wordpress
COPY --from=base /usr/src/wordpress/* /var/www/html

WORKDIR /var/www/html
RUN ls -la


#
# dev stage
#
FROM base AS dev

RUN pecl install \
        xdebug \
    && docker-php-ext-enable \
        xdebug \
    # smoke tests
    && set -ex \
    && ( \
      o=$(php -m | grep "xdebug") \
      && test "$o" = "xdebug" \
    )


#
# prod stage
#
FROM base AS prod

RUN groupadd --gid 2000 wordpress \
    && adduser --shell /bin/true --uid 2000 --gid 2000 --disabled-password --no-create-home --gecos '' wordpress \
    && chown -R wordpress:wordpress /var/www/ \
    # remove world-writeable permissions except for /tmp/
    && find / -xdev -type d -perm /0002 -exec chmod o-w {} + \
    && find / -xdev -type f -perm /0002 -exec chmod o-w {} + \
    && chmod 777 /tmp/ \
    && chown wordpress:root /tmp/ \
    # remove unnecessary accounts, excluding current wordpress and root users
    && sed -i -r '/^(wordpress|root|nobody)/!d' /etc/group \
    && sed -i -r '/^(wordpress|root|nobody)/!d' /etc/passwd \
    # remove interactive login shell for everybody
    && sed -i -r 's#^(.*):[^:]*$#\1:/sbin/nologin#' /etc/passwd \
    # disable password login for everybody
    && ( \
      while IFS=: read -r username _; do passwd -l "$username"; done < /etc/passwd || true \
    ) \
    # remove temporal shadow, passwd and group files
    && find /bin /etc /lib /sbin /usr -xdev -type f -regex ".*-$" -exec rm -f {} + \
    # ensure system dirs are owned by root and not writable by anybody else
    && find /bin /etc /lib /sbin /usr -xdev -type d -exec chown root:root {} \; -exec chmod 0755 {} \; \
    # remove suid & sgid files
    && find /bin /etc /lib /sbin /usr -xdev -type f -a \( -perm /4000 -o -perm /2000 \) -delete \
    # remove unnecessary packages
    && apt remove --purge -y $PHPIZE_DEPS \
    && find / -type f -iname "*apt*" -xdev -delete \
    && find / -type d -iname "*apt*" -print0 -xdev | xargs -0 rm -rf -- \
    # remove potentially risky commands
    && find /bin /etc /lib /sbin /usr -xdev \( \
            -name chgrp -o \
            -name dd -o \
            -name mv -o \
            -name ln -o \
            -name od -o \
            -name strings -o \
            -name shred -o \
            -name su \
        \) -delete \
    # remove any symlinks that we broke during previous steps
    && find /bin /etc /lib /sbin /usr -xdev -type l -exec test ! -e {} \; -delete \
    && rm -rf /root /etc/fstab

COPY ./config/php-fpm.conf /usr/local/etc/php-fpm.conf
COPY ./config/www.conf /usr/local/etc/php-fpm.d/www.conf
COPY ./config/php.ini /usr/local/etc/php.ini
COPY ./config/supervisord.conf /etc/supervisor/supervisord.conf
COPY --chown=wordpress:wordpress ./config/wp-config.php /var/www/html/wp-config.php
