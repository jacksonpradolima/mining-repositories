#!/bin/sh

# Create folder
mkdir -p /mnt/NAS/japlima/mining-repositories/raw_data

# Download
echo "$(date '+%d-%m-%Y %H:%M') [Start] Download Travis Snapshot"
wget https://travistorrent.testroots.org/dumps/travistorrent_8_2_2017.csv.gz -P /mnt/NAS/japlima/mining-repositories/raw_data
echo "$(date '+%d-%m-%Y %H:%M') [Finish] Download Travis Snapshot"

#Unzip
echo "$(date '+%d-%m-%Y %H:%M') [Start] Unzip Travis Snapshot"
gunzip /mnt/NAS/japlima/mining-repositories/raw_data/travistorrent_8_2_2017.csv.gz
echo "$(date '+%d-%m-%Y %H:%M') [Finish] Unzip Travis Snapshot"

# add to gitignore
find . -size +90M | cat >> .gitignore