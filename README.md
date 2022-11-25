# Setup
Create a .env file like so:

TOKEN=\<notion-token\>
PROD_DB=\<notion-db-id\>
DEV_DB=\<notion-db-id\>

# Usage
Run with Makefile, e.g. to insert 2 entries into the Spanish dev db starting at second 10:

`make es_dev SEC=10 MAX=2`
