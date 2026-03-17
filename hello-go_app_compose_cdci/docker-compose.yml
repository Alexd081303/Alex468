services:
  go_app:
    build:
      context: ./docker/
      tags:
        - "linhbngo/go_server:latest"
    container_name: go_app
    image: linhbngo/go_server:latest
    restart: always
    expose:
      - 8080
    ports:
      - 8080:8080
      
  watchtower:
    container_name: watchtower
    image: containrrr/watchtower
    environment:
      - WATCHTOWER_CLEANUP=true
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 30 go_app
