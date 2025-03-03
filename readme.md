

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

# Overview
========

Welcome to Astronomer! This project was generated after you ran 'astro dev init' using the Astronomer CLI. This readme describes the contents of the project, as well as how to run Apache Airflow on your local machine.

Project Contents
================

Your Astro project contains the following files and folders:

- dags: This folder contains the Python files for your Airflow DAGs. By default, this directory includes one example DAG:
    - `example_astronauts`: This DAG shows a simple ETL pipeline example that queries the list of astronauts currently in space from the Open Notify API and prints a statement for each astronaut. The DAG uses the TaskFlow API to define tasks in Python, and dynamic task mapping to dynamically print a statement for each astronaut. For more on how this DAG works, see our [Getting started tutorial](https://www.astronomer.io/docs/learn/get-started-with-airflow).
- Dockerfile: This file contains a versioned Astro Runtime Docker image that provides a differentiated Airflow experience. If you want to execute other commands or overrides at runtime, specify them here.
- include: This folder contains any additional files that you want to include as part of your project. It is empty by default.
- packages.txt: Install OS-level packages needed for your project by adding them to this file. It is empty by default.
- requirements.txt: Install Python packages needed for your project by adding them to this file. It is empty by default.
- plugins: Add custom or community plugins for your project to this file. It is empty by default.
- airflow_settings.yaml: Use this local-only file to specify Airflow Connections, Variables, and Pools instead of entering them in the Airflow UI as you develop DAGs in this project.

Deploy Your Project Locally
===========================

1. Start Airflow on your local machine by running 'astro dev start'.

This command will spin up 4 Docker containers on your machine, each for a different Airflow component:

- Postgres: Airflow's Metadata Database
- Webserver: The Airflow component responsible for rendering the Airflow UI
- Scheduler: The Airflow component responsible for monitoring and triggering tasks
- Triggerer: The Airflow component responsible for triggering deferred tasks

2. Verify that all 4 Docker containers were created by running 'docker ps'.

Note: Running 'astro dev start' will start your project with the Airflow Webserver exposed at port 8080 and Postgres exposed at port 5432. If you already have either of those ports allocated, you can either [stop your existing Docker containers or change the port](https://www.astronomer.io/docs/astro/cli/troubleshoot-locally#ports-are-not-available-for-my-local-airflow-webserver).

3. Access the Airflow UI for your local Airflow project. To do so, go to http://localhost:8080/ and log in with 'admin' for both your Username and Password.

You should also be able to access your Postgres Database at 'localhost:5432/postgres'.

Deploy Your Project to Astronomer
=================================

If you have an Astronomer account, pushing code to a Deployment on Astronomer is simple. For deploying instructions, refer to Astronomer documentation: https://www.astronomer.io/docs/astro/deploy-code/

Contact
=======

The Astronomer CLI is maintained with love by the Astronomer team. To report a bug or suggest a change, reach out to our support.
