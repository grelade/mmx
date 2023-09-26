#/bin/bash

if [ "$CLUSTER_RUN_MODE" = "single" ]; then
    python server.py --mongodb_url=${MONGODB_URL} --run_mode ${CLUSTER_RUN_MODE} --job_interval ${CLUSTER_JOB_INTERVAL} --batch_size ${CLUSTER_BATCH_SIZE}
elif [ "$CLUSTER_RUN_MODE" = "continuous" ]; then
    watchmedo auto-restart -p \"*.py\" -- python server.py --mongodb_url=${MONGODB_URL} --run_mode ${CLUSTER_RUN_MODE} --job_interval ${CLUSTER_JOB_INTERVAL} --batch_size ${CLUSTER_BATCH_SIZE}
fi
