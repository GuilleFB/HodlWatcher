#!/bin/bash
# wait-for-it.sh: Waits for a service to become available before running a command.

# Default values
TIMEOUT=30
STRICT=0
HOST=""
PORT=""

# Print usage
usage() {
  echo "Usage: $0 host:port [-t timeout] [-s] [-h]"
  echo "  -t timeout   Timeout in seconds (default is 30)"
  echo "  -s           Strict mode (exit non-zero if the service isn't available)"
  echo "  -h           Show this help message"
}

# Parse arguments
while getopts "t:sh" opt; do
  case "$opt" in
    t) TIMEOUT=$OPTARG ;;
    s) STRICT=1 ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

shift $((OPTIND-1))

# Get host and port from the first argument
HOST=$1
PORT=$(echo $HOST | sed -e 's/^.*://')
HOST=$(echo $HOST | sed -e 's/:.*//')

if [ -z "$HOST" ] || [ -z "$PORT" ]; then
  echo "Error: You must specify both a host and a port in the format host:port."
  usage
  exit 1
fi

# Wait until the service is available
echo "Waiting for $HOST:$PORT to be available..."
for i in $(seq 1 $TIMEOUT); do
  nc -z "$HOST" "$PORT" && break
  echo "Waiting... $i/$TIMEOUT"
  sleep 1
done

# If not available, exit with error code
if [ $i -gt $TIMEOUT ]; then
  echo "Error: $HOST:$PORT is still not available after $TIMEOUT seconds."
  if [ $STRICT -eq 1 ]; then
    exit 1
  else
    exit 0
  fi
else
  echo "$HOST:$PORT is available!"
fi
