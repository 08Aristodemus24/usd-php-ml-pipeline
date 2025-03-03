FROM apache/airflow:2.10.5

USER root

# Install OpenJDK-17
RUN apt update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get install -y ant && \
    apt-get clean;

# Set JAVA_HOME
# if in macos use 
# ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-arm64/
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64/
RUN export JAVA_HOME

USER airflow

# install needed dependencies in airflow container
RUN \
# pip install apache-airflow \
pip install apache-airflow-providers-apache-spark \
apache-airflow-providers-common-compat \
apache-airflow-providers-amazon \
pyspark 