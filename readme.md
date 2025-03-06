

# This is my first data engineering project aiming to create data pipeline to extract eeg signals, transform them into usable features, and load the tables into a data warehouse.

# Usage:
1. clone repository with `git clone https://github.com/08Aristodemus24/data-pipeline-1`
2. navigate to directory with `readme.md` and `requirements.txt` file
3. run command; `conda create -n <name of env e.g. data-pipeline-1> python=3.12.3`. Note that 3.12.3 must be the python version otherwise packages to be installed would not be compatible with a different python version
4. once environment is created activate it by running command `conda activate`
5. then run `conda activate data-pipeline-1`
6. check if pip is installed by running `conda list -e` and checking list
7. if it is there then move to step 8, if not then install `pip` by typing `conda install pip`
8. if `pip` exists or install is done run `pip install -r requirements.txt` in the directory you are currently in
9. install jdk-17 and java 8 for apache spark
10. install airflow using this `pip install "apache-airflow[celery]==2.10.4" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.4/constraints-3.12.txt"`


# Insights:
* error may occur once airflow is installed in the environment especially in a windows os 
```
C:\Users\LARRY\anaconda3\envs\data-pipeline-1\Lib\site-packages\airflow\__init__.py:36: RuntimeWarning: Airflow currently can be run on POSIX-compliant Operating Systems. For development, it is regularly tested on fairly modern Linux Distros and recent versions of macOS. On Windows you can run it via WSL2 (Windows Subsystem for Linux 2) or via Linux Containers. The work to add Windows support is tracked via https://github.com/apache/airflow/issues/10388, but it is not a high priority.
  warnings.warn(
OSError while attempting to symlink the latest log directory
```
to solve this we need to install a linux runtime environment in order to use airflow since airflow is built for a linux os 
* in order to access amazon webservices programmatically you'd need to create a identity and access management (IAM) user, IAM is another amazon web service like EC2, S3, EMR, SageMaker, etc. that allows you to access these other services programmatically . Once you've created your IAM user you need to click the user you created go to security credentials tab and under the access keys section click create access keys, which will give you options like `**Local code** You plan to use this access key to enable application code in a local development environment to access your AWS account.`; this is the main option you must choose as this describes the situation where you are to read and write onto other amazon web services programmatically case on point from airflow. Once done store safely the `aws secret access key` and your `aws access key` in your `.env` file for now 

* docker-compose build
* `docker build -t <name of image e.g. eda-denoiser-stress-detector> .`
* `docker images` lists all the built images
* `docker image rm <id or name of image>`
* `docker run -p <unused port like 80 in local machine>:<unused port in container like 80> -it <image name or id>`
* to echo ocntents of file in bash terminal run `cat <name of file>.<file ext>`
* we could also enter an images container to run bash commands and see what files are in the container e.g. `docker run -it <image name or id> bash`   


# Tools that I might use:
* Apache Airflow - data orchestration, workflow, and manager for steps in the data pipeline
* Snowflake/Databricks - for data warehousing
* Apache Spark (PySpark)/DBT (data build tool) - for transforming the raw eeg signals into usable features
* Amazon S3 - store raw eeg, and the transformed features

# Resources:
## Videos:
* building a data pipeline using airflow, apache spark, emr, & snowflake: https://youtu.be/hK4kPvJawv8?si=4n4rkcgdzB26fasQ
* free tools used for data engineering projects: https://www.youtube.com/watch?v=M7eGUM28Ke4&list=PLCBT00GZN_SAzwTS-SuLRM547_4MUHPuM&index=28&pp=gAQBiAQB
* sql window functions intermediate mysql: https://www.youtube.com/watch?v=7NBt0V8ebGk&list=PLCBT00GZN_SAzwTS-SuLRM547_4MUHPuM&index=2
* sql window functions rank dense rank lead lag: https://www.youtube.com/watch?v=Ww71knvhQ-s&list=PLCBT00GZN_SAzwTS-SuLRM547_4MUHPuM&index=1&t=1189s&pp=gAQBiAQB

## Articles:
* https://stackoverflow.com/questions/47811129/requests-in-python-is-not-downloading-file-completely
* https://realpython.com/python-download-file-from-url/
* pyspark and aws s3: https://medium.com/@bharadwajaryan30/handling-big-data-with-pyspark-and-aws-s3-f2a3f28419a9
* installing and configuring apache airflow: https://medium.com/orchestras-data-release-pipeline-blog/installing-and-configuring-apache-airflow-a-step-by-step-guide-5ff602c47a36
* moving average: https://learnsql.com/blog/moving-average-in-sql/

# Data sources:
* motor imagery eeg: http://gigadb.org/dataset/100295
* database for ecg signals: https://physionet.org/about/database/
* healthcare data api: https://data.cms.gov/provider-data/search
* kaggle eeg features: https://www.kaggle.com/code/huvinh/eeg-extract-features
* book api: 
* https://openlibrary.org/dev/docs/api/books
* https://openlibrary.org/developers/api
* forex trades: https://polygon.io/docs/forex/getting-started
- keep an eye on forexTicker/currency pair since it has the attributes/columns you need for every time interval (e.g. day) such as closing price, opening price, highest price, lowest price, and volume all of which you can use for signal processing
* stock trades data: https://polygon.io/docs/stocks/
- keep an eye on tickers parameter since it represents the companys short name apple inc. for instance is short for AAPL and you can use this for the tickers parameter
* list of tickers in the stock market: https://stockanalysis.com/stocks/

we want ot get previous stocks from the last years let's say, and continue getting the stock or forex OHLC (open, high, low, close) for the coming days or depending what time interval you want

let's say we want to get the C:USDPHP
