#/bin/bash

if [ "$SCRAPE_RUN_MODE" = "single" ]; then
    python server.py --mongodb_url=${MONGODB_URL} --run_mode ${SCRAPE_RUN_MODE} --job_interval ${SCRAPE_JOB_INTERVAL}
elif [ "$SCRAPE_RUN_MODE" = "continuous" ]; then
    watchmedo auto-restart -p \"*.py\" -- python server.py --mongodb_url=${MONGODB_URL} --run_mode ${SCRAPE_RUN_MODE} --job_interval ${SCRAPE_JOB_INTERVAL}
fi
