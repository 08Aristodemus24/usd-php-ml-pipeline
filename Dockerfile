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

# switch to airflow user right after setting env variables
USER airflow

# copy and install dependencies in airflow container
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

