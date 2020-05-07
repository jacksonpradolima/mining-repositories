#!/bin/sh

#ls /mnt/NAS/japlima/mining-repositories/raw_data/buildlogs | parallel -j 10 ruby /mnt/NAS/japlima/travistorrent-tools/bin/buildlog_analysis.rb "/mnt/NAS/japlima/mining-repositories/raw_data/buildlogs/{}"

ls /mnt/NAS/japlima/mining-repositories/raw_data/buildlogs | parallel -j 10 ruby bin/buildlog_analysis.rb "/mnt/NAS/japlima/mining-repositories/raw_data/buildlogs/{}"