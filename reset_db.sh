#!/bin/bash

echo 'removing db...'
rm fog.db
rm cloud.db
echo 'creating db...'
touch fog.db
touch cloud.db
echo 'creating tables...'
python create_table_script.py

echo 'DB resetted!'