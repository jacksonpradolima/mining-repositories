#!/bin/sh

ls raw_data/buildlogs | parallel -j 10 ruby ../travistorrent-tools/bin/buildlog_analysis.rb "raw_data/buildlogs/{}"