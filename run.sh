#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 [dev | prod] [<server>]"
    echo "Options:"
    echo "  <server>       Specify server to run [api, scrape, all]"
}

if [ $# -ge 2 ]; then
    if [ "$1" = "dev" ]; then
        env_file=".env.dev"
        yaml_file="compose-dev.yaml"
        add=""
    elif [ "$1" = "prod" ]; then
        env_file=".env"
        yaml_file="compose.yaml"
        add="nginx"
    fi

    server=$2
    if [ "$server" = "scrape" ]; then
        docker compose --env-file $env_file --file $yaml_file up scrape feat_extract --detach
    elif [ "$server" = "api" ]; then
        docker compose --env-file $env_file --file $yaml_file up api $add --detach
    elif [ "$server" = "all" ]; then
        docker compose --env-file $env_file --file $yaml_file up --detach
    fi
else
    usage
fi