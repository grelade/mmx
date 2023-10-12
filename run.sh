#!/bin/bash

# Default values for options
server=""

# Function to display usage information
usage() {
    echo "Usage: $0 [-s <server>]"
    echo "Options:"
    echo "  -s <server>       Specify server to run [api, scrape, all]"
    exit 1
}

# Parse command-line options
while getopts "s:" opt; do
    case "$opt" in
        s) server="$OPTARG";;
        \?) echo "Invalid option: -$OPTARG" >&2
            usage;;
    esac
done

# Check if required options are provided
if [ -z "$server" ]; then
    echo "You must specify the server with -s option."
    usage
fi

if [ "$server" = "scrape" ]; then
    docker compose up scrape feat_extract --detach
elif [ "$server" = "api" ]; then
    docker compose up api nginx --detach
elif [ "$server" = "all" ]; then
    docker compose up --detach
fi
