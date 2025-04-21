#!/bin/sh


echo "HOST  = '$WORD_SORT_SERVER_HOST'"
echo "PORT  = '$WORD_SORT_SERVER_PORT'"

python ./lab2/word_sort_server.py \
  --host "${WORD_SORT_SERVER_HOST}" \
  --port "${WORD_SORT_SERVER_PORT}"