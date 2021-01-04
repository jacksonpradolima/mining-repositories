[<img align="right" src="https://cdn.buymeacoffee.com/buttons/default-orange.png" width="217px" height="51x">](https://www.buymeacoffee.com/pradolima)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)


# Mining Repositories

![](https://img.shields.io/badge/python-3.6+-blue.svg)


This repository contains methods to mining feature information for each test case over commits from a git repository.

1. **Main Process**  (```main.py```) iterate over commits from a git repository to extract the features of each test case available (in the commit), such as **Test Case Name**, **Test Size**, **Cyclomatic Complexity**, and **Change Type**.
2. **Post Processing**  (```main_post.py```) this process replace all zeros by the previous nonzero value. This is necessary for the **Test Size** and **Cyclomatic Complexity** that are not always available.

# Features Available

The tool aims to extract the following data:

- **Test Case Age (TcAge)**: This feature measures how long the test case exists and is given by a number which is incremented for each new CI Cycle in that the test case appears;    
- **Test User-Preference (TUP)**: Test case importance given by the tester. In this case, this feature is based on user-preference. For this feature, we randomly selects a percentage (10%, 50%, and 80%) of failing test cases in each commit;
- **Test Case Change (ChangeType)**: Considers whether a test case changed. If a test case is changed from a commit to another, there is a high probability that the alteration was performed because some change in the software needs to be tested. If the test case was changed, we could detect and consider if the test case was renamed, or it added or removed some methods;
- **Cyclomatic Complexity (McCabe)**: This feature considers the complexity of McCabe. High complexity can be related to a more elaborated test case;
- **Test Size (SLOC)**: TThe SLOC metric counts the lines but excludes empty lines and comments. This is sometimes referred to as the source lines of code (SLOC). In literature this is often also referred as physical lines of code.

Such a features are merged with features already extracted in Travis Torrent tool:

- **Test Case Duration (Duration)**: The time spent by a test case to execute;
- **Number of Test Ran Methods (NumRan)**: The number of test methods executed during the test, considering that some test methods are not executed due to some previous test method(s) have been failed;
- **Number of Test Failed Methods (NumErrors)**: The number of test methods which failed during the test. This is different from the reward given by RNFail function, which take only two values: 1 or 0. As we do not have any information about correlation failure, we assume large number of failed test methods have higher probability to detect different failures.


# :red_circle: Installing required dependencies

The following command allows to install the required dependencies:

```
 $ pip install -r requirements.txt
 ```

 External packages used in this tool to extract features are:

 - [metrics](https://github.com/markfink/metrics)
 - [PyDriller](https://github.com/ishepard/pydriller)

# :heavy_exclamation_mark: Preparation

Before running the tool, please make the `git clone` for each dataset (repository) under evaluation. Now, the tool does not clone a repository. Besides that, cloning repositories before running this tool allow avoiding overhead.

#  Using the tool <img width="40" src="https://emojis.slackmojis.com/emojis/images/1609352144/11926/dianajoa.gif?1609352144" alt="Dianajoa" />

## 📌 Running the feature extraction process (*Main Process*)

To extract the features, do:

``` console
python main.py --project_dir PathToDatasets --clone_dir PathToCloneDatasets --datasets ListOfDatasets
``` 
where

``` console
    --project_dir                    Path to datasets where we can find the 'data-filtered.csv' file
    --clone_dir                      Path to folder where the repositories were cloned
    --datasets                       List of datasets, in which represents a folder inside 'project_dir' and 'clone_dir' directories. For instance, alibaba@druid alibaba@fastjson
    -o, --output_dir                 Local to save the results. Default 'results/features/'
```

## 📌 Running the post processing (*Post Processing*)

Once that the features were extract, do:

``` console
python main_post.py --feature_dir results/features/ --datasets alibaba@druid alibaba@fastjson
```

where

``` console
    --feature_dir                    Path to results where the features were saved    
    --datasets                       List of datasets, in which represents a folder inside 'feature_dir' directory. For instance, alibaba@druid alibaba@fastjson
    -o, --output_dir                 Local to save the results after post processing. Default 'results/features_post/'
```

## Possible Problems that you can find:

1. Some commits are unnavailble. This occurs because git cannot "pull" (obtain) the source code from a commit. This is a problem from git.
2. Due to problem #1, we recommend to execute the **Post Processing** to fill the gaps in the features.  

# Contributors

- 👨‍💻 Jackson Antonio do Prado Lima <a href="mailto:jacksonpradolima@gmail.com">:e-mail:</a>
