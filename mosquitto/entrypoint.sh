#!/bin/sh
set -e

PASSWD_FILE=/mosquitto/config/passwd

if [ -n "$MOSQUITTO_USERNAME" ] && [ -n "$MOSQUITTO_PASSWORD" ]; then
    if [ ! -f "$PASSWD_FILE" ]; then
        mosquitto_passwd -c -b "$PASSWD_FILE" "$MOSQUITTO_USERNAME" "$MOSQUITTO_PASSWORD"
    else
        mosquitto_passwd -b "$PASSWD_FILE" "$MOSQUITTO_USERNAME" "$MOSQUITTO_PASSWORD"
    fi
    chown mosquitto:mosquitto "$PASSWD_FILE"
fi

ACL_FILE=/mosquitto/config/mosquitto.acl
if [ -f "$ACL_FILE" ]; then
    chown mosquitto:mosquitto "$ACL_FILE" 2>/dev/null
    chmod 0700 "$ACL_FILE" 2>/dev/null
fi

exec "$@"
