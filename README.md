# wahoo2dawarich

This is a tool to sync wahoo fitness data to DaWarIch.
It uses the dropbox docker container to fetch the data. You must configure dropbox at wahoo.


Please add the following block to: docker-compose file in DaWarIch

```yaml
service:
....
  dropbox:
    image: otherguy/dropbox:latest
    environment:
      - TZ=Europe/Berlin
      - DROPBOX_UID=1000
      - DROPBOX_GID=1000
      - POLLING_INTERVAL=20
    volumes:
      - dropbox_cfg:/opt/dropbox/.dropbox
      - dropbox_data:/opt/dropbox/Dropbox
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'    # Limit CPU usage to 50% of one core
  wahoo2dawarich:
     image: ghcr.io/tabacha/wahoo2dawarich:main
     volumes:
       - dropbox_data:/dropbox
       - dawarich_watched:/dawarich
     environment:
       - DROPBOX_DIR=/dropbox/Apps/WahooFitness/
       - DEST_DIR=/dawarich/mail@example.com
     restart: unless-stopped
     deploy:
      resources:
        limits:
          cpus: '1'    # Limit CPU usage to 50% of one core

volumes:
    ...
    dropbox_cfg:
    dropbox_data:
```


To link Dropbox to your account, check the logs of the Docker container to retrieve the Dropbox authentication URL:

$ docker compose logs --follow dropbox

If you have problems with authentication the dropbox container, please look at:

https://github.com/otherguy/docker-dropbox/issues/73#issuecomment-2551769147
