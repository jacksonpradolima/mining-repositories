# mining-repositories

### Preparation

Clone this repository into a local directory. Under this directory, create the subdirectories `data` and `raw-data`.


------



This repository contains data analysis scripts used in the paper "Sentiment Analysis of Travis CI Builds" by Rodrigo Souza (UFBA) and Bruno Silva (UNIFACS), presented at the 14th International Conference on Mining Software Repositories -- May 20-21, 2017. Buenos Aires, Argentina.

## Dependencies

- SQLite
- Ruby, with the following gems:
    - git
    - sqlite
- R, with the following packages: 
    - data.table
    - dplyr
    - effsize
    - ggplot2
    - knitr
    - orddom
    - RSQLite
    - SnowballC
    - stringr
    - vcd

## Steps

To reproduce the results in the paper, you'll need to get information from repository, get build information, extract sentiment, and finally run the analysis.

### Preparation

Clone this repository into a local directory. Under this directory, create the subdirectories `data` and `raw-data`.

### Get information from repository

Clone all git repositories into directories named `user__project`, replacing `user` by the repository owner and `project` by the project name. Example: The repository at <https://github.com/ReactiveX/rxjs> needs to be cloned into a directory named `ReactiveX__rxjs`

Run `commit-log/gitlob.rb DBPATH REPOPATH`. This script reads all repositories under the path `REPOPATH`, extracts the commit log for each repository and writes them into the SQLite database located at the path `DBPATH` (please replace `REPOPATH` and `DBPATH` with actual paths).

### Get build information

Download <https://travistorrent.testroots.org/dumps/travistorrent_8_2_2017.csv.gz> to the `raw-data/` directory (the directory needs to be created).

Run `src/convert-travis-csv-to-sqlite.R` to convert the downloaded file into `.rds`, a file format optimized for R.

### Extract sentiment

Download the SentiStrength data at <http://sentistrength.wlv.ac.uk/> (you'll need to fill in a form)

Download the SentiStrength Java tool at <http://gateway.path.berkeley.edu:8080/artifactory/list/release-local/com/sentistrength/sentistrength/0.1/sentistrength-0.1.jar>

Move SentiStrength's files into the a subdirectory of this repository's directory named `sentistrength`. Move the data files to a subdirectory `sentistrength/SentStrength_Data`.

Run `src/filter-wordlist.R` (using R) to filter software-specific words from SentiStrength's data files.

Go to `sentistrength` and run the following command to extract commit messages from the SQLite database to a text file:

```bash
sqlite3 PATH-TO-COMMIT-LOG.sqlite "select replace(replace(message, char(13), ' '), char(10), ' ') from commits order by project, sha;" > bli
```

Run the following command to compute the sentiment for each commit message in the text file:

```bash
java -jar sentistrength-0.1.jar sentidata SentStrength_Data/ input ./bli explain
```

Rename the output to `bli2_out.txt` and use `gzip` to compress it to `bli2_out.txt.gz`.

### Run the analysis

Using R, run the following scripts under the `src` directory:

1. `convert-sentistrength.R` - to convert SentiStrength's output to an SQLite database
2. `merge-travis-senti.R` - to merge all the data into a single R data frame
3. `analyze.R` - compute statistics, plot graphs, and test hypotheses
