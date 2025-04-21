#!/bin/sh


echo "WORD_SORT_SERVER_HOST  = '$WORD_SORT_SERVER_HOST'"
echo "WORD_SORT_SERVER_PORT  = '$WORD_SORT_SERVER_PORT'"

echo "CITIES_SERVER_HOST  = '$CITIES_SERVER_HOST'"
echo "CITIES_SERVER_PORT  = '$CITIES_SERVER_PORT'"

python ./lab2/word_sort_server.py \
  --host "${WORD_SORT_SERVER_HOST}" \
  --port "${WORD_SORT_SERVER_PORT}" &

python ./lab3/server.py \
  --host "${CITIES_SERVER_HOST}" \
  --port "${CITIES_SERVER_PORT}"