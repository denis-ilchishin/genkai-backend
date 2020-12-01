DUMP_NAME="$(date +'%A_%H-%M')"
pg_dump $POSTGRES_DB -f $DUMPS_DIR/$DUMP_NAME.sql.tar -F tar -U $POSTGRES_USER