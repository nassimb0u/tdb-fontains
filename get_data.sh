#!/bin/bash

data=$(wget -qO- "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/fontaines-a-boire/exports/json?lang=fr&timezone=Europe%2FBerlin")
timestamp=$(date +"%Y-%m-%dT%H:%M:%S%:z")

file_name="drinking_fontains ${timestamp}.json"
path=${1:-~/drinking_fontains_data}
echo $data > "${path}/${file_name}"
# python venvwrapper
workon projet-sds
python3 script.py
