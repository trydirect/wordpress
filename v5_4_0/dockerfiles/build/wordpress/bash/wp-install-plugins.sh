#!/usr/bin/env bash

# ===============================================================================
# Bash Script - Install WordPress plugins
#
# Based on the plugin list, download each plugin and save them to
# `/var/www/html/wp-content/plugins`.
#
# And then update `wp-config.php` file.
#
# ===============================================================================


# ----------------------------------------------------------
# Define plugins to be installed
#
# ----------------------------------------------------------

# Add plugin's "code name" into `PLUGINS` variable.
read -r -d '' PLUGINS << ENDL
nginx-helper
ENDL


# Loop into the `PLUGINS` and download each plugin
# The target path is `/var/www/html/wp-content/plugins`
for PLUG in $PLUGINS; do
	echo "---Download WP plugin: ${PLUG} --->"
	curl -s -O $(curl -i -s https://wordpress.org/plugins/${PLUG}/ | egrep -o "https://downloads.wordpress.org/plugin/[^']+")
	find . -type f -name "*.zip" -print0 | xargs -0 -I % unzip -q -o % -d /var/www/html/wp-content/plugins
	#unzip -o *.zip -d /var/www/html/wp-content/plugins
	chown -R wordpress:wordpress /var/www/html/wp-content/plugins
done

# Activate the plugin - nginx-helper
echo "---Activate WP Plugin - nginx-helper--->"
cat << ENDL >> /var/www/html/wp-config.php

/** Activate plugins */
\$plugins = get_option( 'active_plugins' );
if ( count( \$plugins ) === 0 ) {
  require_once(ABSPATH .'/wp-admin/includes/plugin.php');
  \$pluginsToActivate = array( 'nginx-helper/nginx-helper.php' );
  foreach ( \$pluginsToActivate as \$plugin ) {
    if ( !in_array( \$plugin, \$plugins ) ) {
      activate_plugin( '/var/www/html/wp-content/plugins/' . \$plugin );
    }
  }
}
ENDL

chown wordpress:wordpress /var/www/html/wp-config.php
