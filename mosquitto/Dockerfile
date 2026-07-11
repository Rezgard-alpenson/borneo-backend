FROM eclipse-mosquitto:latest

COPY entrypoint.sh /entrypoint.sh
COPY mosquitto.acl /mosquitto/config/mosquitto.acl

RUN chmod +x /entrypoint.sh && \
    chown mosquitto:mosquitto /mosquitto/config/mosquitto.acl && \
    chmod 0700 /mosquitto/config/mosquitto.acl

ENTRYPOINT ["/entrypoint.sh"]
CMD ["mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]
