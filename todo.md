- how airflow.cfg can be utilized for environment variables
- add spark services in docker compose file
- what if I imittate the docker compose file of the begineer de project?
- add connections through airflow.cfg file

# Insights:
1. the way to use shell/bash/linux commands in a docker container is listing the running containers first using `docker ps`. Take the container (mini VM) you want to enter and enter `docker exec -it <container id or name> <sh | bash>`. Once you're inside the container's shell, you can execute any commands available within the container's environment e.g. 
```
ls -l
pwd
python --version
```
Below is a walkthrough of using the bash terminal inside a running docker container which would be our airflow-webserver running on port 8080. Other containers running separate from the airflow-webserver would be the airflow-triggerer and the airflow-scheduler.

```
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows
```

# This is when we run the `docker ps` command to see the running containers after running the `docker compose up` command
```
PS C:\Users\LARRY> docker ps
CONTAINER ID   IMAGE                             COMMAND                  CREATED         STATUS                        PORTS                    NAMES
c0069bbf3f75   data-pipeline-airflow-triggerer   "/usr/bin/dumb-init …"   2 minutes ago   Up About a minute (healthy)   8080/tcp                 data-pipeline-airflow-triggerer-1
8343c7aa37b1   data-pipeline-airflow-webserver   "/usr/bin/dumb-init …"   2 minutes ago   Up About a minute (healthy)   0.0.0.0:8080->8080/tcp   data-pipeline-airflow-webserver-1
c8c1026dde3a   data-pipeline-airflow-scheduler   "/usr/bin/dumb-init …"   2 minutes ago   Up About a minute (healthy)   8080/tcp                
 data-pipeline-airflow-scheduler-1
40535ebb8613   postgres:13                       "docker-entrypoint.s…"   2 minutes ago   Up 2 minutes (healthy)        5432/tcp                
 data-pipeline-postgres-1
```


PS C:\Users\LARRY> docker network

Usage:  docker network COMMAND

Manage networks

Commands:
  connect     Connect a container to a network
  create      Create a network
  disconnect  Disconnect a container from a network
  inspect     Display detailed information on one or more networks
  ls          List networks
  prune       Remove all unused networks
  rm          Remove one or more networks

Run 'docker network COMMAND --help' for more information on a command.

# This is when we run the docker network ls command to see the networks that house our containers
```
PS C:\Users\LARRY>docker network ls
NETWORK ID     NAME                    DRIVER    SCOPE
48900335d64d   bridge                  bridge    local
3962bd44a1c5   data-pipeline_default   bridge    local
86bd2adfefc0   host                    host      local
29ba87cd8ae0   none                    null      local
```

# Here let's say we wanted to 
PS C:\Users\LARRY>docker exec -it 8343c7aa37b1 bash
airflow@8343c7aa37b1:/opt/airflow$ $AIRFLOW_HOME
bash: /opt/airflow: Is a directory
airflow@8343c7aa37b1:/opt/airflow$ls
airflow-webserver.pid  config  dags  include  logs  plugins  webserver_config.py
airflow@8343c7aa37b1:/opt/airflow$cd config
airflow@8343c7aa37b1:/opt/airflow/config$ls
airflow.cfg
airflow@8343c7aa37b1:/opt/airflow/config$airflow.cfg
bash: airflow.cfg: command not found
airflow@8343c7aa37b1:/opt/airflow/config$cat airflow.cfg
# airflow@8343c7aa37b1:/opt/airflow/config$
airflow@8343c7aa37b1:/opt/airflow/config$cd ..
airflow@8343c7aa37b1:/opt/airflow$cd dags
airflow@8343c7aa37b1:/opt/airflow/dags$ls
__pycache__  forex_ml_pipeline.py  operators  utilities
airflow@8343c7aa37b1:/opt/airflow/dags$less forex_ml_pipeline.py
bash: less: command not found
airflow@8343c7aa37b1:/opt/airflow/dags$cat forex_ml_pipeline.py
import sys
import datetime as dt
import os
import shutil
import time
import boto3

from pathlib import Path

from airflow import DAG, settings
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable, Connection
from airflow.configuration import conf
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

from utilities.preprocessors import reformat_date
from operators.create_s3_bucket import create_s3_bucket
from operators.pull_forex_data import pull_forex_data
from operators.test_pull_forex_data import test_pull_forex_data
from operators.transform_forex_data import transform_forex_data

from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import (
    LocalFilesystemToS3Operator,
)
from airflow.providers.amazon.aws.transfers.sql_to_s3 import SqlToS3Operator


# go to this site if you want to use cron instead of datetime to set schedule_interval
# https://crontab.guru/#00_12_*_*_Sun



# def get_env_vars(ti):
#     """
#     push api key to xcom so that pull_forex_data can access
#     this xcom
#     """
#     api_key = Variable.get("POLYGON_API_KEY")

#     ti.xcom_push(key="api_key", value=api_key)

# get airflow folder
airflow_home = conf.get('core', 'dags_folder')

# base dir would be /usr/local/airflow/
BASE_DIR = Path(airflow_home).resolve().parent

# data dir once joined with base dir would be /usr/local/airflow/include/data/
DATA_DIR = os.path.join(BASE_DIR, 'include/data')

# bucket name
BUCKET_NAME = "usd-php-ml-pipeline-bucket"

default_args = {
    'owner': 'mikhail',
    'retries': 3,
    'retry_delay': dt.timedelta(minutes=2)
}

with DAG(
    dag_id="forex_ml_pipeline",
    default_args=default_args,
    description="pull forex of usd to php data from last january 1 2024 up to january 2025 in intervals of 4 hours",
    start_date=dt.datetime(2024, 1, 1, 12),

    # runs every sunday at 12:00
    schedule_interval="00 12 * * Sun",
    catchup=False
) as dag:

    # get_env_vars_task = PythonOperator(
    #     task_id="get_env_vars",
    #     python_callable=get_env_vars
    # )

    # create_s3_bucket_task = PythonOperator(
    #     task_id='create_s3_bucket',
    #     python_callable=create_s3_bucket,
    #     op_kwargs={
    #         'region': 'us-east-2',
    #         'bucket-name': BUCKET_NAME,
    #     }
    # )

    pull_forex_data_task = PythonOperator(
        task_id='pull_forex_data',
        python_callable=test_pull_forex_data,
        # python_callable=pull_forex_data,
        op_kwargs={
            # "start_date": "january 1 2024",
            # "end_date": "january 1 2025",
            # "ticker": "C:USDPHP",
            # "multiplier": 4,
            # "timespan": "hour",
            "formatter": reformat_date,
            "save_path": DATA_DIR
        }
    )

    transform_forex_data_task = SparkSubmitOperator(
        task_id='transform_forex_data',
        conn_id='my_spark_conn',
        application='./dags/operators/transform_forex_data.py',

        # pass argument vector to spark submit job operator since
        # it is a file that runs like a script
        application_args=["{{ti.xcom_pull(key='new_file_path', task_ids='pull_forex_data')}}"],
        # application_args=["{{ti.xcom_pull(key='file_path', task_ids='pull_forex_data')}}"],
        verbose=True
    )

    pull_forex_data_task >> transform_forex_data_taskairflow@8343c7aa37b1:/opt/airflow/dags$
airflow@8343c7aa37b1:/opt/airflow/dags$cd ../
airflow@8343c7aa37b1:/opt/airflow$

with this knowledge we can know what airflow commands can we run that might reveal to us how to better interact with it and debug errors in the future



try

1. `pip list --format=freeze`
```
pip list --format=freeze
adal==1.2.7
adlfs==2024.12.0
aiobotocore==2.19.0
aiofiles==23.2.1
aiohappyeyeballs==2.4.4
aiohttp==3.11.11
aioitertools==0.12.0
aiomysql==0.2.0
aiosignal==1.3.2
aiosqlite==0.20.0
alembic==1.14.1
amqp==5.3.1
annotated-types==0.7.0
anyio==4.8.0
apache-airflow==2.10.5
apache-airflow-providers-amazon==9.2.0
apache-airflow-providers-apache-spark==5.0.0
apache-airflow-providers-celery==3.10.0
apache-airflow-providers-cncf-kubernetes==10.1.0
apache-airflow-providers-common-compat==1.3.0
apache-airflow-providers-common-io==1.5.0
apache-airflow-providers-common-sql==1.21.0
apache-airflow-providers-docker==4.0.0
apache-airflow-providers-elasticsearch==6.0.0
apache-airflow-providers-fab==1.5.2
apache-airflow-providers-ftp==3.12.0
apache-airflow-providers-google==12.0.0
apache-airflow-providers-grpc==3.7.0
apache-airflow-providers-hashicorp==4.0.0
apache-airflow-providers-http==5.0.0
apache-airflow-providers-imap==3.8.0
apache-airflow-providers-microsoft-azure==12.0.0
apache-airflow-providers-mysql==6.0.0
apache-airflow-providers-odbc==4.9.0
apache-airflow-providers-openlineage==2.0.0
apache-airflow-providers-postgres==6.0.0
apache-airflow-providers-redis==4.0.0
apache-airflow-providers-sendgrid==4.0.0
apache-airflow-providers-sftp==5.0.0
apache-airflow-providers-slack==9.0.0
apache-airflow-providers-smtp==1.9.0
apache-airflow-providers-snowflake==6.0.0
apache-airflow-providers-sqlite==4.0.0
apache-airflow-providers-ssh==4.0.0
apispec==6.8.1
argcomplete==3.5.3
asgiref==3.8.1
asn1crypto==1.5.1
asyncpg==0.30.0
asyncssh==2.19.0
attrs==25.1.0
Authlib==1.3.1
azure-batch==14.2.0
azure-common==1.1.28
azure-core==1.32.0
azure-cosmos==4.9.0
azure-datalake-store==0.0.53
azure-identity==1.19.0
azure-keyvault-secrets==4.9.0
azure-kusto-data==4.6.3
azure-mgmt-containerinstance==10.1.0
azure-mgmt-containerregistry==10.3.0
azure-mgmt-core==1.5.0
azure-mgmt-cosmosdb==9.7.0
azure-mgmt-datafactory==9.1.0
azure-mgmt-datalake-nspkg==3.0.1
azure-mgmt-datalake-store==0.5.0
azure-mgmt-nspkg==3.0.2
azure-mgmt-resource==23.2.0
azure-mgmt-storage==22.0.0
azure-nspkg==3.0.2
azure-servicebus==7.13.0
azure-storage-blob==12.24.1
azure-storage-file-datalake==12.18.1
azure-storage-file-share==12.20.1
azure-synapse-artifacts==0.19.0
azure-synapse-spark==0.7.0
babel==2.17.0
backoff==2.2.1
bcrypt==4.2.1
beautifulsoup4==4.13.0
billiard==4.2.1
blinker==1.9.0
boto3==1.36.3
botocore==1.36.3
cachelib==0.9.0
cachetools==5.5.1
cattrs==24.1.2
celery==5.4.0
certifi==2025.1.31
cffi==1.17.1
chardet==5.2.0
charset-normalizer==3.4.1
click==8.1.8
click-didyoumean==0.3.1
click-plugins==1.1.1
click-repl==0.3.0
clickclick==20.10.2
colorama==0.4.6
colorlog==6.9.0
ConfigUpdater==3.2
connexion==2.14.2
cron-descriptor==1.4.5
croniter==6.0.0
cryptography==42.0.8
db-dtypes==1.4.0
decorator==5.1.1
Deprecated==1.2.18
dill==0.3.9
distlib==0.3.9
dnspython==2.7.0
docker==7.1.0
docstring_parser==0.16
elastic-transport==8.17.0
elasticsearch==8.17.1
email_validator==2.2.0
eventlet==0.39.0
filelock==3.17.0
Flask==2.2.5
Flask-AppBuilder==4.5.2
Flask-Babel==2.0.0
Flask-Caching==2.3.0
Flask-JWT-Extended==4.7.1
Flask-Limiter==3.10.1
Flask-Login==0.6.3
Flask-Session==0.5.0
Flask-SQLAlchemy==2.5.1
Flask-WTF==1.2.2
flower==2.0.1
frozenlist==1.5.0
fsspec==2025.2.0
gcloud-aio-auth==5.3.2
gcloud-aio-bigquery==7.1.0
gcloud-aio-storage==9.3.0
gcsfs==2025.2.0
gevent==24.11.1
google-ads==25.1.0
google-analytics-admin==0.23.3
google-api-core==2.24.1
google-api-python-client==2.160.0
google-auth==2.38.0
google-auth-httplib2==0.2.0
google-auth-oauthlib==1.2.1
google-cloud-aiplatform==1.79.0
google-cloud-alloydb==0.4.1
google-cloud-appengine-logging==1.5.0
google-cloud-audit-log==0.3.0
google-cloud-automl==2.15.0
google-cloud-batch==0.17.33
google-cloud-bigquery==3.20.1
google-cloud-bigquery-datatransfer==3.18.0
google-cloud-bigtable==2.28.1
google-cloud-build==3.29.0
google-cloud-compute==1.24.0
google-cloud-container==2.55.1
google-cloud-core==2.4.1
google-cloud-datacatalog==3.24.1
google-cloud-dataflow-client==0.8.15
google-cloud-dataform==0.5.14
google-cloud-dataplex==2.6.0
google-cloud-dataproc==5.16.0
google-cloud-dataproc-metastore==1.17.0
google-cloud-dlp==3.26.0
google-cloud-kms==3.2.2
google-cloud-language==2.16.0
google-cloud-logging==3.11.4
google-cloud-memcache==1.11.0
google-cloud-monitoring==2.26.0
google-cloud-orchestration-airflow==1.16.1
google-cloud-os-login==2.16.0
google-cloud-pubsub==2.28.0
google-cloud-redis==2.17.0
google-cloud-resource-manager==1.14.0
google-cloud-run==0.10.14
google-cloud-secret-manager==2.22.1
google-cloud-spanner==3.51.0
google-cloud-speech==2.30.0
google-cloud-storage==2.19.0
google-cloud-storage-transfer==1.15.0
google-cloud-tasks==2.18.0
google-cloud-texttospeech==2.24.0
google-cloud-translate==3.19.0
google-cloud-videointelligence==2.15.0
google-cloud-vision==3.9.0
google-cloud-workflows==1.16.0
google-crc32c==1.6.0
google-re2==1.1.20240702
google-resumable-media==2.7.2
googleapis-common-protos==1.66.0
graphviz==0.20.3
greenlet==3.1.1
grpc-google-iam-v1==0.14.0
grpc-interceptor==0.15.4
grpcio==1.70.0
grpcio-gcp==0.2.2
grpcio-status==1.62.3
gunicorn==23.0.0
h11==0.14.0
h2==4.2.0
hpack==4.1.0
httpcore==1.0.7
httplib2==0.22.0
httpx==0.27.0
humanize==4.11.0
hvac==2.3.0
hyperframe==6.1.0
idna==3.10
ijson==3.3.0
immutabledict==4.2.1
importlib-metadata==6.11.0
inflection==0.5.1
isodate==0.7.2
itsdangerous==2.2.0
Jinja2==3.1.5
jmespath==0.10.0
json-merge-patch==0.2
jsonpath-ng==1.7.0
jsonschema==4.23.0
jsonschema-specifications==2024.10.1
kombu==5.4.2
kubernetes==30.1.0
kubernetes_asyncio==30.1.0
lazy-object-proxy==1.10.0
ldap3==2.9.1
limits==4.0.1
linkify-it-py==2.0.3
lockfile==0.12.2
looker-sdk==25.0.0
lxml==5.3.0
Mako==1.3.8
markdown-it-py==3.0.0
MarkupSafe==3.0.2
marshmallow==3.26.0
marshmallow-oneofschema==3.1.1
marshmallow-sqlalchemy==0.28.2
mdit-py-plugins==0.4.2
mdurl==0.1.2
methodtools==0.4.7
microsoft-kiota-abstractions==1.3.3
microsoft-kiota-authentication-azure==1.1.0
microsoft-kiota-http==1.3.3
microsoft-kiota-serialization-json==1.0.0
microsoft-kiota-serialization-text==1.0.0
more-itertools==10.6.0
msal==1.31.1
msal-extensions==1.2.0
msgraph-core==1.2.1
msrest==0.7.1
msrestazure==0.6.4.post1
multidict==6.1.0
mysql-connector-python==9.2.0
mysqlclient==2.2.7
numpy==1.26.4
oauthlib==3.2.2
openlineage-integration-common==1.27.0
openlineage-python==1.27.0
openlineage_sql==1.27.0
opentelemetry-api==1.27.0
opentelemetry-exporter-otlp==1.27.0
opentelemetry-exporter-otlp-proto-common==1.27.0
opentelemetry-exporter-otlp-proto-grpc==1.27.0
opentelemetry-exporter-otlp-proto-http==1.27.0
opentelemetry-proto==1.27.0
opentelemetry-sdk==1.27.0
opentelemetry-semantic-conventions==0.48b0
ordered-set==4.1.0
packaging==24.2
pandas==2.1.4
pandas-gbq==0.26.1
paramiko==3.5.0
pathspec==0.12.1
pendulum==3.0.0
pip==25.0
platformdirs==4.3.6
pluggy==1.5.0
ply==3.11
portalocker==2.10.1
prison==0.2.1
prometheus_client==0.21.1
prompt_toolkit==3.0.50
propcache==0.2.1
proto-plus==1.26.0
protobuf==4.25.6
psutil==6.1.1
psycopg2-binary==2.9.10
py4j==0.10.9.7
pyarrow==19.0.0
pyasn1==0.6.1
pyasn1_modules==0.4.0
PyAthena==3.12.2
pycparser==2.22
pydantic==2.10.6
pydantic_core==2.27.2
pydata-google-auth==1.9.1
Pygments==2.19.1
PyJWT==2.10.1
PyMySQL==1.1.1
PyNaCl==1.5.0
pyodbc==5.2.0
pyOpenSSL==24.3.0
pyparsing==3.2.1
pyspark==3.5.4
python-daemon==3.1.2
python-dateutil==2.9.0.post0
python-dotenv==1.0.1
python-http-client==3.3.7
python-ldap==3.4.4
python-nvd3==0.16.0
python-slugify==8.0.4
python3-saml==1.16.0
pytz==2025.1
PyYAML==6.0.2
redis==5.2.1
redshift-connector==2.1.5
referencing==0.36.2
requests==2.32.3
requests-oauthlib==1.3.1
requests-toolbelt==1.0.0
rfc3339-validator==0.1.4
rich==13.9.4
rich-argparse==1.6.0
rpds-py==0.22.3
rsa==4.9
s3transfer==0.11.2
scramp==1.4.5
sendgrid==6.11.0
setproctitle==1.3.4
setuptools==75.8.0
shapely==2.0.7
six==1.17.0
slack_sdk==3.34.0
sniffio==1.3.1
snowflake-connector-python==3.13.2
snowflake-sqlalchemy==1.7.3
sortedcontainers==2.4.0
soupsieve==2.6
SQLAlchemy==1.4.54
sqlalchemy-bigquery==1.12.1
SQLAlchemy-JSONField==1.0.2
sqlalchemy-spanner==1.8.0
SQLAlchemy-Utils==0.41.2
sqlparse==0.5.3
sshtunnel==0.4.0
starkbank-ecdsa==2.2.0
statsd==4.0.1
std-uritemplate==2.0.1
tabulate==0.9.0
tenacity==9.0.0
termcolor==2.5.0
text-unidecode==1.3
time-machine==2.16.0
tomlkit==0.13.2
tornado==6.4.2
typing_extensions==4.12.2
tzdata==2025.1
uc-micro-py==1.0.3
universal_pathlib==0.2.6
uritemplate==4.1.1
urllib3==2.3.0
uv==0.5.24
vine==5.1.0
virtualenv==20.29.1
watchtower==3.3.1
wcwidth==0.2.13
websocket-client==1.8.0
Werkzeug==2.2.3
wirerope==1.0.0
wrapt==1.17.2
WTForms==3.2.1
xmlsec==1.3.14
yarl==1.18.3
zipp==3.21.0
zope.event==5.0
zope.interface==7.2
```

2. `python`
```
airflow@8343c7aa37b1:/opt/airflow$ python
Python 3.12.9 (main, Feb  6 2025, 22:37:05) [GCC 12.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
>>> exit()
```

3. `airflow`
```
Usage: airflow [-h] GROUP_OR_COMMAND ...

Positional Arguments:
  GROUP_OR_COMMAND

    Groups
      config            View configuration
      connections       Manage connections
      dags              Manage DAGs
      db                Database operations
      jobs              Manage jobs
      pools             Manage pools
      providers         Display providers
      roles             Manage roles
      tasks             Manage tasks
      users             Manage users
      variables         Manage variables

    Commands:
      cheat-sheet       Display cheat sheet
      dag-processor     Start a standalone Dag Processor instance
      info              Show information about current Airflow and environment
      kerberos          Start a kerberos ticket renewer
      plugins           Dump information about loaded plugins
      rotate-fernet-key
                        Rotate encrypted connection credentials and variables
      scheduler         Start a scheduler instance
      standalone        Run an all-in-one copy of Airflow
      sync-perm         Update permissions for existing roles and optionally DAGs
      triggerer         Start a triggerer instance
      version           Show the version
      webserver         Start a Airflow webserver instance

Options:
  -h, --help            show this help message and exit

airflow command error: the following arguments are required: GROUP_OR_COMMAND, see help above.
```

4. `airflow version`
```
airflow@8343c7aa37b1:/opt/airflow$ airflow version
2.10.5
```

5. `pip`
```
airflow@8343c7aa37b1:/opt/airflow$ pip

Usage:
  pip <command> [options]

Commands:
  install                     Install packages.
  download                    Download packages.
  uninstall                   Uninstall packages.
  freeze                      Output installed packages in requirements format.
  inspect                     Inspect the python environment.
  list                        List installed packages.
  show                        Show information about installed packages.
  check                       Verify installed packages have compatible dependencies.
  config                      Manage local and global configuration.
  search                      Search PyPI for packages.
  cache                       Inspect and manage pip's wheel cache.
  index                       Inspect information available from package indexes.
  wheel                       Build wheels from your requirements.
  hash                        Compute hashes of package archives.
  completion                  A helper command used for command completion.
  debug                       Show information useful for debugging.
  help                        Show help for commands.

General Options:
  -h, --help                  Show help.
  --debug                     Let unhandled exceptions propagate outside the main subroutine, instead of logging them
                              to stderr.
  --isolated                  Run pip in an isolated mode, ignoring environment variables and user configuration.
  --require-virtualenv        Allow pip to only run in a virtual environment; exit with an error otherwise.
  --python <python>           Run pip with the specified Python interpreter.
  -v, --verbose               Give more output. Option is additive, and can be used up to 3 times.
  -V, --version               Show version and exit.
  -q, --quiet                 Give less output. Option is additive, and can be used up to 3 times (corresponding to
                              WARNING, ERROR, and CRITICAL logging levels).
  --log <path>                Path to a verbose appending log.
  --no-input                  Disable prompting for input.
  --keyring-provider <keyring_provider>
                              Enable the credential lookup via the keyring library if user input is allowed. Specify
                              which mechanism to use [auto, disabled, import, subprocess]. (default: auto)
  --proxy <proxy>             Specify a proxy in the form scheme://[user:passwd@]proxy.server:port.
  --retries <retries>         Maximum number of retries each connection should attempt (default 5 times).
  --timeout <sec>             Set the socket timeout (default 15 seconds).
  --exists-action <action>    Default action when a path already exists: (s)witch, (i)gnore, (w)ipe, (b)ackup,
                              (a)bort.
  --trusted-host <hostname>   Mark this host or host:port pair as trusted, even though it does not have valid or any
                              HTTPS.
  --cert <path>               Path to PEM-encoded CA certificate bundle. If provided, overrides the default. See 'SSL
                              Certificate Verification' in pip documentation for more information.
  --client-cert <path>        Path to SSL client certificate, a single file containing the private key and the
                              certificate in PEM format.
  --cache-dir <dir>           Store the cache data in <dir>.
  --no-cache-dir              Disable the cache.
  --disable-pip-version-check
                              Don't periodically check PyPI to determine whether a new version of pip is available for
                              download. Implied with --no-index.
  --no-color                  Suppress colored output.
  --no-python-version-warning
                              Silence deprecation warnings for upcoming unsupported Pythons.
  --use-feature <feature>     Enable new functionality, that may be backward incompatible.
  --use-deprecated <feature>  Enable deprecated functionality, that will be removed in the future.
```

6. `airflow connections add spark-conn --conn-host spark://spark-master --conn-type spark --conn-port 7077`. An important thing to note is that it is important to know what container you are in where this command is executed because this command is better suited to run in the `airflow-webserver` container, as opposed to the `airflow-triggerer` and `airflow-scheduler` since the webserver runs on port `8080`.

```
airflow@8343c7aa37b1:/opt/airflow$ airflow connections add spark-conn --conn-host spark://spark-master --conn-type spark --conn-port 7077
[2025-02-24T02:13:52.712+0000] {providers_manager.py:287} INFO - Optional provider feature disabled when importing 'airflow.providers.google.leveldb.hooks.leveldb.LevelDBHook' from 'apache-airflow-providers-google' package
Successfully added `conn_id`=spark-conn : spark://:@spark://spark-master:7077
```

7. what I think I can do is use a script that sets up the connections

8. solve
```
airflow-init-1       | ....................
airflow-init-1       | ERROR! Maximum number of retries (20) reached.
airflow-init-1       |
airflow-init-1       | Last check result:
airflow-init-1       | $ airflow db check
airflow-init-1       | [2025-02-24T11:27:02.906+0000] {cli_action_loggers.py:177} WARNING - Failed to log action (psycopg2.OperationalError) could not translate host name "postgres" to address: Temporary failure in name resolution
airflow-init-1       |
airflow-init-1       | (Background on this error at: https://sqlalche.me/e/14/e3q8)
service "airflow-init" didn't complete successfully: exit 1
```

or

```
airflow-init-1       | Traceback (most recent call last):
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3371, in _wrap_pool_connect
airflow-init-1       |     return fn()
airflow-init-1       |            ^^^^
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 327, in connect
airflow-init-1       |     return _ConnectionFairy._checkout(self)
airflow-init-1       |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 894, in _checkout
airflow-init-1       |     fairy = _ConnectionRecord.checkout(pool)
airflow-init-1       |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 493, in checkout
airflow-init-1       |     rec = pool._do_get()
airflow-init-1       |           ^^^^^^^^^^^^^^
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/pool/impl.py", line 145, in _do_get
airflow-init-1       |     with util.safe_reraise():
airflow-init-1       |          ^^^^^^^^^^^^^^^^^^^
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py", line 70, in __exit__
airflow-init-1       |     compat.raise_(
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/util/compat.py", line 211, in raise_
airflow-init-1       |     raise exception
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/pool/impl.py", line 143, in _do_get
airflow-init-1       |     return self._create_connection()
airflow-init-1       |            ^^^^^^^^^^^^^^^^^^^^^^^^^
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 273, in _create_connection
airflow-init-1       |     return _ConnectionRecord(self)
airflow-init-1       |            ^^^^^^^^^^^^^^^^^^^^^^^
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 388, in __init__
airflow-init-1       |     self.__connect()
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 690, in __connect
airflow-init-1       |     with util.safe_reraise():
airflow-init-1       |          ^^^^^^^^^^^^^^^^^^^
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py", line 70, in __exit__
airflow-init-1       |     compat.raise_(
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/util/compat.py", line 211, in raise_
airflow-init-1       |     raise exception
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 686, in __connect
airflow-init-1       |     self.dbapi_connection = connection = pool._invoke_creator(self)
airflow-init-1       |                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/engine/create.py", line 574, in connect
airflow-init-1       |     return dialect.connect(*cargs, **cparams)
airflow-init-1       |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
airflow-init-1 exited with code 1
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 598, in connect
airflow-init-1       |     return self.dbapi.connect(*cargs, **cparams)
airflow-init-1       |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
airflow-init-1       |   File "/home/airflow/.local/lib/python3.12/site-packages/psycopg2/__init__.py", line 122, in connect
airflow-init-1       |     conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
airflow-init-1       |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
airflow-init-1       | psycopg2.OperationalError: could not translate host name "postgres" to address: Name or service not known
```
error

insgights on the error:
The error message you're seeing in the airflow-init service indicates a problem with the service's ability to connect to the PostgreSQL database. Specifically, it's a name resolution issue.

Root Cause:

DNS Resolution Failure: The error "could not translate host name "postgres" to address: Temporary failure in name resolution" means that the airflow-init container cannot resolve the hostname postgres to an IP address. This usually happens when the container's DNS service is not working correctly, or the container is not properly connected to the Docker network where the postgres service is running.
Troubleshooting Steps:

Verify Network Configuration:

Check docker-compose.yaml: Make sure that both the airflow-init and postgres services are connected to the same Docker network. In your docker-compose.yaml, it should look something like this:

.yaml
```
services:
  postgres:
    # ... other configurations ...
    networks:
      - michael

  airflow-init:
    # ... other configurations ...
    networks:
      - michael

networks:
  michael:
    driver: bridge  # Or other appropriate driver
```
Inspect Network: You can inspect the network to see if the containers are connected:

Bash

docker network inspect michael
Look for the Containers section to verify that both postgres and airflow-init are listed.

Ensure postgres Service is Running:

Check Container Status: Verify that the postgres container is running and healthy:

Bash

docker ps
Look for the postgres container in the list. Its status should be "Up" or "healthy".

Check Logs: If the postgres container is not running or healthy, check its logs for errors:

Bash

`docker logs <postgres_container_name_or_id>`
Check depends_on:

Verify depends_on: Ensure that the airflow-init service has a depends_on clause for the postgres service and that the condition is set to service_healthy. This will ensure that the airflow-init service starts only after the postgres service is healthy.

.yaml
```
services:
  airflow-init:
    # ... other configurations ...
    depends_on:
      postgres:
        condition: service_healthy
```
DNS Issues:

Restart Docker: If you suspect a DNS issue with Docker, try restarting the Docker service:

Bash

sudo systemctl restart docker  # Linux
# Or restart Docker Desktop on Windows/macOS
Check Host DNS: Ensure that your host machine's DNS settings are working correctly.

Timing Issue:

Delay Start: In some cases, the postgres service might take a bit longer to become fully available. You can try adding a small delay to the airflow-init service startup using a command or entrypoint script.
Example of Corrected airflow-init Section:

.yaml
```
services:
  airflow-init:
    <<: *airflow-common
    entrypoint: /bin/bash
    command:
      - -c
      - |
        sleep 5  # Add a 5-second delay
        if [[ -z "${AIRFLOW_UID}" ]]; then
          # ... rest of the init script ...
        fi
        # ... rest of the init script ...
    # ... other configurations ...
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - michael
```
Steps to Apply:

Verify network setup.
Ensure postgres is running.
Check depends_on.
If needed, restart Docker or check host DNS.
If needed, add a delay to airflow-init startup.
Run docker-compose down and then docker-compose up -d --build to apply changes.
By following these steps, you should be able to identify and resolve the name resolution issue and get your airflow-init service working correctly.

articles:
* resolving "could not translate host name "postgres" to address" when connecting from one container to another using container name": https://stackoverflow.com/questions/61805951/docker-how-to-fix-could-not-translate-host-name-postgres-to-address-when-co
* this may be because airflow-init and spark are not on the same network (but now I know it is because postgres is not on the same network as the spark services and airflow services containers)

```
(base) C:\Users\LARRY\Documents\Scripts\data-pipeline>docker network ls
NETWORK ID     NAME                    DRIVER    SCOPE
6525aaaf4d94   bridge                  bridge    local
30cfe7e15441   data-pipeline_default   bridge    local
135217477b14   data-pipeline_michael   bridge    local
86bd2adfefc0   host                    host      local
29ba87cd8ae0   none                    null      local

(base) C:\Users\LARRY\Documents\Scripts\data-pipeline>docker network inspect data-pipeline_michael
[
    {
        "Name": "data-pipeline_michael",
        "Id": "135217477b14cf627912c76410e2379bf456e3d5aa2923d8a7eb9b3317140fdc",
        "Created": "2025-02-24T12:07:14.027638284Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": null,
            "Config": [
                {
                    "Subnet": "172.18.0.0/16",
                    "Gateway": "172.18.0.1"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Containers": {
            "603d0b2fb2338fd7716d34ffedda9be0aaa421e7f0ba4225910b6e6834d9d2e2": {
                "Name": "data-pipeline-spark-master-1",
                "EndpointID": "d7bb98790e0fb68e103dbfc6ab26c01b4d59c271099d04cb0eae962b8505491f",
                "MacAddress": "02:42:ac:12:00:02",
                "IPv4Address": "172.18.0.2/16",
                "IPv6Address": ""
            },
            "8837561e9dc1ac30cb61d4a1396b488f72cd7031bcbb2ce335c6fb4320db8e97": {
                "Name": "data-pipeline-spark-worker-1",
                "EndpointID": "598f8d62e7c6eb6bbd68d7fa1784b36b70767a95cfa00ba2af98e5e8903322b0",
                "MacAddress": "02:42:ac:12:00:03",
                "IPv4Address": "172.18.0.3/16",
                "IPv6Address": ""
            }
        },
        "Options": {},
        "Labels": {
            "com.docker.compose.config-hash": "e07080de0b40a16a6bc9290a6fec8393cecdf9c75193fbb497773860e2b96a7c",
            "com.docker.compose.network": "michael",
            "com.docker.compose.project": "data-pipeline",
            "com.docker.compose.version": "2.31.0"
        }
    }
]

(base) C:\Users\LARRY\Documents\Scripts\data-pipeline>docker network inspect data-pipeline_default
[
    {
        "Name": "data-pipeline_default",
        "Id": "30cfe7e154413ca2b8de7a413724ae5b2c3f897f5fec716c2a13c4dc24534646",
        "Created": "2025-02-24T12:07:14.071032332Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": null,
            "Config": [
                {
                    "Subnet": "172.19.0.0/16",
                    "Gateway": "172.19.0.1"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Containers": {
            "962672f79f2b20d6cc5e4d38c42aa08feff10af1ef29478b8b3028a05a8dde84": {
                "Name": "data-pipeline-postgres-1",
                "EndpointID": "6ae2de42fd43c7849d24865742e8d54858bdfa1a2a76cb754b0687029c9b3264",
                "MacAddress": "02:42:ac:13:00:02",
                "IPv4Address": "172.19.0.2/16",
                "IPv6Address": ""
            }
        },
        "Options": {},
        "Labels": {
            "com.docker.compose.config-hash": "f728e80f7205aad87c68ff563e33e7fce696f54ff35947f1b014951b75cf44db",
            "com.docker.compose.network": "default",
            "com.docker.compose.project": "data-pipeline",
            "com.docker.compose.version": "2.31.0"
        }
    }
]
```

so we caught here as we can see we have two separate networks michael and default where the spark master and spark workers containers are running and where the postgres container is running respectively. Clearly postgres is on another network and while the former 2 containers are on another network 

```
...
postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 10s
      retries: 5
      start_period: 5s
    restart: always
...
```

In the snippet this docker compose file we see that the reason  why docker raises the `could not translate host name "postgres" to address" when connecting from one container to another using container name` error is because unlike our other services like airflow and spark these services inherit the `x-airflow-common` and `x-spark-common` network defined for instance through `airflow-webserver: <<: *airflow-common` which in this cases this airflow-webserver conatiner inherits the network of the `x-airflow-common` "parent" container which is michael. And so because a service needs to have its network defined in order for docker to know what network it belongs it needs to be specified and needs to be the same as other services in order for all services/containers to run on the same network. In this case postgres does not inherit a network from any parent and does not also have a network defined. However if we do provide or specify the network the same as all other services/containers networks which in this case is `michael` as can be seen in the example below in the updated docker compose file...

```
version: '3.1'
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

# Basic Airflow cluster configuration for CeleryExecutor with Redis and PostgreSQL.
#
# WARNING: This configuration is for local development. Do not use it in a production deployment.
#
# This configuration supports basic configuration using environment variables or an .env file
# The following variables are supported:
#
# AIRFLOW_IMAGE_NAME           - Docker image name used to run Airflow.
#                                Default: apache/airflow:2.10.5
# AIRFLOW_UID                  - User ID in Airflow containers
#                                Default: 50000
# AIRFLOW_PROJ_DIR             - Base path to which all the files will be volumed.
#                                Default: .
# Those configurations are useful mostly in case of standalone testing/running Airflow in test/try-out mode
#
# _AIRFLOW_WWW_USER_USERNAME   - Username for the administrator account (if requested).
#                                Default: airflow
# _AIRFLOW_WWW_USER_PASSWORD   - Password for the administrator account (if requested).
#                                Default: airflow
# _PIP_ADDITIONAL_REQUIREMENTS - Additional PIP requirements to add when starting all containers.
#                                Use this option ONLY for quick checks. Installing requirements at container
#                                startup is done EVERY TIME the service is started.
#                                A better way is to build a custom image or extend the official image
#                                as described in https://airflow.apache.org/docs/docker-stack/build.html.
#                                Default: ''
#
# Feel free to modify this file to suit your needs.
---
x-airflow-common:
  &airflow-common
  # In order to add custom dependencies or upgrade provider packages you can use your extended image.
  # Comment the image line, place your Dockerfile in the directory where you placed the docker-compose.yaml
  # and uncomment the "build" line below, Then run `docker-compose build` to build the images.
  # image: ${AIRFLOW_IMAGE_NAME:-apache/airflow:2.10.5}
  build: .
  environment:
    &airflow-common-env
    # AIRFLOW__CORE__EXECUTOR: CeleryExecutor
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    # AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    # AIRFLOW__CELERY__BROKER_URL: redis://:@redis:6379/0
    AIRFLOW__CORE__FERNET_KEY: ''
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    AIRFLOW__API__AUTH_BACKENDS: 'airflow.api.auth.backend.basic_auth,airflow.api.auth.backend.session'
    # yamllint disable rule:line-length
    # Use simple http server on scheduler for health checks
    # See https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/logging-monitoring/check-health.html#scheduler-health-check-server
    # yamllint enable rule:line-length
    AIRFLOW__SCHEDULER__ENABLE_HEALTH_CHECK: 'true'
    # WARNING: Use _PIP_ADDITIONAL_REQUIREMENTS option ONLY for a quick checks
    # for other purpose (development, test and especially production usage) build/extend Airflow image.
    _PIP_ADDITIONAL_REQUIREMENTS: ${_PIP_ADDITIONAL_REQUIREMENTS:-}
    # The following line can be used to set a custom config file, stored in the local config folder
    # If you want to use it, outcomment it and replace airflow.cfg with the name of your config file
    AIRFLOW_CONFIG: '/opt/airflow/config/airflow.cfg'
  volumes:
    - ${AIRFLOW_PROJ_DIR:-.}/dags:/opt/airflow/dags
    # - ${AIRFLOW_PROJ_DIR:-.}/logs:/opt/airflow/logs
    - ${AIRFLOW_PROJ_DIR:-.}/config:/opt/airflow/config
    - ${AIRFLOW_PROJ_DIR:-.}/plugins:/opt/airflow/plugins
    - ${AIRFLOW_PROJ_DIR:-.}/include:/opt/airflow/include
  user: "${AIRFLOW_UID:-50000}:0"
  depends_on:
    &airflow-common-depends-on
    # redis:
    #   condition: service_healthy
    postgres:
      condition: service_healthy
  networks:
    - michael

x-spark-common: 
  &spark-common
  image: bitnami/spark:latest
  volumes:
    - ${AIRFLOW_PROJ_DIR:-.}/include:/opt/airflow/include
  networks:
    - michael

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 10s
      retries: 5
      start_period: 5s
    restart: always
    networks:
      - michael

  # redis:
  #   # Redis is limited to 7.2-bookworm due to licencing change
  #   # https://redis.io/blog/redis-adopts-dual-source-available-licensing/
  #   image: redis:7.2-bookworm
  #   expose:
  #     - 6379
  #   healthcheck:
  #     test: ["CMD", "redis-cli", "ping"]
  #     interval: 10s
  #     timeout: 30s
  #     retries: 50
  #     start_period: 30s
  #   restart: always

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8974/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

  # airflow-worker:
  #   <<: *airflow-common
  #   command: celery worker
  #   healthcheck:
  #     # yamllint disable rule:line-length
  #     test:
  #       - "CMD-SHELL"
  #       - 'celery --app airflow.providers.celery.executors.celery_executor.app inspect ping -d "celery@$${HOSTNAME}" || celery --app airflow.executors.celery_executor.app inspect ping -d "celery@$${HOSTNAME}"'
  #     interval: 30s
  #     timeout: 10s
  #     retries: 5
  #     start_period: 30s
  #   environment:
  #     <<: *airflow-common-env
  #     # Required to handle warm shutdown of the celery workers properly
  #     # See https://airflow.apache.org/docs/docker-stack/entrypoint.html#signal-propagation
  #     DUMB_INIT_SETSID: "0"
  #   restart: always
  #   depends_on:
  #     <<: *airflow-common-depends-on
  #     airflow-init:
  #       condition: service_completed_successfully

  airflow-triggerer:
    <<: *airflow-common
    command: triggerer
    healthcheck:
      test: ["CMD-SHELL", 'airflow jobs check --job-type TriggererJob --hostname "$${HOSTNAME}"']
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

  airflow-init:
    <<: *airflow-common
    entrypoint: /bin/bash
    # yamllint disable rule:line-length
    command:
      - -c
      - |
        if [[ -z "${AIRFLOW_UID}" ]]; then
          echo
          echo -e "\033[1;33mWARNING!!!: AIRFLOW_UID not set!\e[0m"
          echo "If you are on Linux, you SHOULD follow the instructions below to set "
          echo "AIRFLOW_UID environment variable, otherwise files will be owned by root."
          echo "For other operating systems you can get rid of the warning with manually created .env file:"
          echo "    See: https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#setting-the-right-airflow-user"
          echo
        fi
        one_meg=1048576
        mem_available=$$(($$(getconf _PHYS_PAGES) * $$(getconf PAGE_SIZE) / one_meg))
        cpus_available=$$(grep -cE 'cpu[0-9]+' /proc/stat)
        disk_available=$$(df / | tail -1 | awk '{print $$4}')
        warning_resources="false"
        if (( mem_available < 4000 )) ; then
          echo
          echo -e "\033[1;33mWARNING!!!: Not enough memory available for Docker.\e[0m"
          echo "At least 4GB of memory required. You have $$(numfmt --to iec $$((mem_available * one_meg)))"
          echo
          warning_resources="true"
        fi
        if (( cpus_available < 2 )); then
          echo
          echo -e "\033[1;33mWARNING!!!: Not enough CPUS available for Docker.\e[0m"
          echo "At least 2 CPUs recommended. You have $${cpus_available}"
          echo
          warning_resources="true"
        fi
        if (( disk_available < one_meg * 10 )); then
          echo
          echo -e "\033[1;33mWARNING!!!: Not enough Disk space available for Docker.\e[0m"
          echo "At least 10 GBs recommended. You have $$(numfmt --to iec $$((disk_available * 1024 )))"
          echo
          warning_resources="true"
        fi
        if [[ $${warning_resources} == "true" ]]; then
          echo
          echo -e "\033[1;33mWARNING!!!: You have not enough resources to run Airflow (see above)!\e[0m"
          echo "Please follow the instructions to increase amount of resources available:"
          echo "   https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#before-you-begin"
          echo
        fi
        mkdir -p /sources/logs /sources/dags /sources/plugins
        chown -R "${AIRFLOW_UID}:0" /sources/{logs,dags,plugins}
        exec /entrypoint airflow version
    # yamllint enable rule:line-length
    environment:
      <<: *airflow-common-env
      _AIRFLOW_DB_MIGRATE: 'true'
      _AIRFLOW_WWW_USER_CREATE: 'true'
      _AIRFLOW_WWW_USER_USERNAME: ${_AIRFLOW_WWW_USER_USERNAME:-airflow}
      _AIRFLOW_WWW_USER_PASSWORD: ${_AIRFLOW_WWW_USER_PASSWORD:-airflow}
      _PIP_ADDITIONAL_REQUIREMENTS: ''
    user: "0:0"
    volumes:
      - ${AIRFLOW_PROJ_DIR:-.}:/sources

  airflow-cli:
    <<: *airflow-common
    profiles:
      - debug
    environment:
      <<: *airflow-common-env
      CONNECTION_CHECK_MAX_COUNT: "0"
    # Workaround for entrypoint issue. See: https://github.com/apache/airflow/issues/16252
    command:
      - bash
      - -c
      - airflow

  spark-master:
    <<: *spark-common
    command: bin/spark-class org.apache.spark.deploy.master.Master
    environment:
      - SPARK_MODE=master
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
      - SPARK_MASTER_WEBUI_PORT=8081
    ports:
      - "8081:8081"
      - "7077:7077"

  spark-worker:
    <<: *spark-common
    command: bin/spark-class org.apache.spark.deploy.worker.Worker spark://spark-master:7077
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_MEMORY=2G
      - SPARK_WORKER_CORES=2
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
    depends_on:
      - spark-master
    
  # You can enable flower by adding "--profile flower" option e.g. docker-compose --profile flower up
  # or by explicitly targeted on the command line e.g. docker-compose up flower.
  # See: https://docs.docker.com/compose/profiles/
  # flower:
  #   <<: *airflow-common
  #   command: celery flower
  #   profiles:
  #     - flower
  #   ports:
  #     - "5555:5555"
  #   healthcheck:
  #     test: ["CMD", "curl", "--fail", "http://localhost:5555/"]
  #     interval: 30s
  #     timeout: 10s
  #     retries: 5
  #     start_period: 30s
  #   restart: always
  #   depends_on:
  #     <<: *airflow-common-depends-on
  #     airflow-init:
  #       condition: service_completed_successfully

networks:
  michael:

volumes:
  postgres-db-volume:
```

Should we run this, the services such as airflow-webserver, airflow-triggerer, airflow-scheduler, spark-master, spark-worker, and postgres would all finally run on the same network called `michael`. And if we check this by running `docker network ls` we see that no more network other than the one we defined called michael should be present here unlike when we didn't specify the network of the postgres service and when we ran the `docker compose up` the networks present were two, those being `data-pipeline_michael` and `data-pipeline_default` which was where the postgres service/container was running on.


```
(base) C:\Users\LARRY\Documents\Scripts\data-pipeline>docker network ls
NETWORK ID     NAME                    DRIVER    SCOPE
a3f744b65add   bridge                  bridge    local
e0258378e2c8   data-pipeline_michael   bridge    local
b71e12365e2c   host                    host      local
0e4dd26c4c33   none                    null      local

(base) C:\Users\LARRY\Documents\Scripts\data-pipeline>docker network inspect data-pipeline_michael
[
    {
        "Name": "data-pipeline_michael",
        "Id": "e0258378e2c85955c03d388800f0a9afe5e3432ece5f03026aaff9a69251d5c9",
        "Created": "2025-03-01T06:45:42.548324084Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": null,
            "Config": [
                {
                    "Subnet": "172.18.0.0/16",
                    "Gateway": "172.18.0.1"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Containers": {
            "20b5e60865432b2820375791875cb05b63cdc84be7feb9aa02708c4c6e263973": {
                "Name": "data-pipeline-postgres-1",
                "EndpointID": "944115c693a4aad198ee01b5dfb1c5700eadaad8458b0eabf820ca495c5419e8",
                "MacAddress": "02:42:ac:12:00:02",
                "IPv4Address": "172.18.0.2/16",
                "IPv6Address": ""
            },
            "4a5aeb90df32bd0efc72dbabe73b14a3ecfd0d141b311c71673f3a5a4ab8387b": {
                "Name": "data-pipeline-spark-worker-1",
                "EndpointID": "e483496f0ff5a32232f220926f700b166e411cc4de1cd85c6044768dda1951bc",
                "MacAddress": "02:42:ac:12:00:04",
                "IPv4Address": "172.18.0.4/16",
                "IPv6Address": ""
            },
            "a69a947abb0f0f62eeacb9903a34b81468b04d763dc99b84a50688921682d975": {
                "Name": "data-pipeline-airflow-webserver-1",
                "EndpointID": "b61944297167d6ded5b135c522217c3479549e36c31b01beaf4c57feefaf2f63",
                "MacAddress": "02:42:ac:12:00:05",
                "IPv4Address": "172.18.0.5/16",
                "IPv6Address": ""
            },
            "baa3f85f73625f6823d77d250feb171ed2a6dea021910197b782a1d1822af017": {
                "Name": "data-pipeline-airflow-scheduler-1",
                "EndpointID": "acd1698db4690e5145f172369cd5e633001011701968c161d59e02924ead3337",
                "MacAddress": "02:42:ac:12:00:07",
                "IPv4Address": "172.18.0.7/16",
                "IPv6Address": ""
            },
            "d29d6cc5e4c48b8e82be5c2788fb18c8e2d3a7b20d43d3ea1961bfd724b0a040": {
                "Name": "data-pipeline-airflow-triggerer-1",
                "EndpointID": "9015f14f49cca3923a5bd8993b94e9aff66c21c835b2f7d5da8716722ae4bcfb",
                "MacAddress": "02:42:ac:12:00:06",
                "IPv4Address": "172.18.0.6/16",
                "IPv6Address": ""
            },
            "dcfe67bde34b70e8d704aa3a9b71ae1781a9333d8e377f4948a4c0d17ead3690": {
                "Name": "data-pipeline-spark-master-1",
                "EndpointID": "ba6c751b430372a9aec8b9876c2b7303fd0a527b9f35e57bf936091c25c8a6a5",
                "MacAddress": "02:42:ac:12:00:03",
                "IPv4Address": "172.18.0.3/16",
                "IPv6Address": ""
            }
        },
        "Options": {},
        "Labels": {
            "com.docker.compose.config-hash": "e07080de0b40a16a6bc9290a6fec8393cecdf9c75193fbb497773860e2b96a7c",
            "com.docker.compose.network": "michael",
            "com.docker.compose.project": "data-pipeline",
            "com.docker.compose.version": "2.31.0"
        }
    }
]

(base) C:\Users\LARRY\Documents\Scripts\data-pipeline>
```

So in the end all we have to do is to let the service eitherr inherit a parent containers network or specify it explicitly. 

* To print an environment variable inside a docker container all we again have to do is enter the docker container via `docker exec -it <container id or name> bash` 

```
(base) C:\Users\LARRY\Documents\Scripts\data-pipeline>docker exec -it a69a947abb0f bash
airflow@a69a947abb0f:/opt/airflow$ echo $AIRFLOW_HOME
/opt/airflow
airflow@a69a947abb0f:/opt/airflow$ echo $JAVA_HOME
/usr/lib/jvm/java-17-openjdk-amd64/
airflow@a69a947abb0f:/opt/airflow$
```

This allows us to see what environment variables are inside the docker container

* to see all environment variables in a docker container (which is basically seeing what environment variables are in this mini virtual machine we have) we run printenv
```
airflow@a69a947abb0f:/opt/airflow$ printenv
UV_CACHE_DIR=/tmp/.cache/uv
PYTHON_SHA256=7220835d9f90b37c006e9842a8dff4580aaca4318674f947302b8d28f3f81112
DUMB_INIT_SETSID=1
HOSTNAME=a69a947abb0f
PYTHON_VERSION=3.12.9
LANGUAGE=C.UTF-8
JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64/
AIRFLOW_USER_HOME_DIR=/home/airflow
ADDITIONAL_RUNTIME_APT_DEPS=
PWD=/opt/airflow
AIRFLOW_VERSION=2.10.5
AIRFLOW__CORE__LOAD_EXAMPLES=false
AIRFLOW__API__AUTH_BACKENDS=airflow.api.auth.backend.basic_auth,airflow.api.auth.backend.session
INSTALL_MSSQL_CLIENT=true
INSTALL_MYSQL_CLIENT_TYPE=mariadb
GUNICORN_CMD_ARGS=--worker-tmp-dir /dev/shm
HOME=/home/airflow
LANG=C.UTF-8
LS_COLORS=rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=00:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc=01;31:*.arj=01;31:*.taz=01;31:*.lha=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.tzo=01;31:*.t7z=01;31:*.zip=01;31:*.z=01;31:*.dz=01;31:*.gz=01;31:*.lrz=01;31:*.lz=01;31:*.lzo=01;31:*.xz=01;31:*.zst=01;31:*.tzst=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.alz=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.cab=01;31:*.wim=01;31:*.swm=01;31:*.dwm=01;31:*.esd=01;31:*.avif=01;35:*.jpg=01;35:*.jpeg=01;35:*.mjpg=01;35:*.mjpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.webp=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:*~=00;90:*#=00;90:*.bak=00;90:*.old=00;90:*.orig=00;90:*.part=00;90:*.rej=00;90:*.swp=00;90:*.tmp=00;90:*.dpkg-dist=00;90:*.dpkg-old=00;90:*.ucf-dist=00;90:*.ucf-new=00;90:*.ucf-old=00;90:*.rpmnew=00;90:*.rpmorig=00;90:*.rpmsave=00;90:
VIRTUAL_ENV=/home/airflow/.local
AIRFLOW_HOME=/opt/airflow
GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
AIRFLOW_USE_UV=false
AIRFLOW__CORE__EXECUTOR=LocalExecutor
COMMIT_SHA=223b0a4b61a44a83895371b2c9a3a5cafa5df8ea
PIP_CACHE_DIR=/tmp/.cache/pip
AIRFLOW_PIP_VERSION=25.0
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=true
TERM=xterm
ADDITIONAL_RUNTIME_APT_COMMAND=
AIRFLOW_UV_VERSION=0.5.24
_PIP_ADDITIONAL_REQUIREMENTS=
INSTALL_POSTGRES_CLIENT=true
SHLVL=1
LC_MESSAGES=C.UTF-8
RUNTIME_APT_DEPS=
RUNTIME_APT_COMMAND=echo
LD_LIBRARY_PATH=/usr/local/lib
LC_CTYPE=C.UTF-8
AIRFLOW__SCHEDULER__ENABLE_HEALTH_CHECK=true
PS1=\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\u@\h:\w\$
AIRFLOW_INSTALLATION_METHOD=
AIRFLOW_CONFIG=/opt/airflow/config/airflow.cfg
LC_ALL=C.UTF-8
INSTALL_MYSQL_CLIENT=true
PATH=/root/bin:/home/airflow/.local/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
PYTHON_BASE_IMAGE=python:3.12-slim-bookworm
AIRFLOW_UID=50000
BUILD_ID=
AIRFLOW__CORE__FERNET_KEY=
DEBIAN_FRONTEND=noninteractive
_=/usr/bin/printenv
airflow@a69a947abb0f:/opt/airflow$
```

note all these environmentn variables when you want to echo it in the terminal you would use `echo $<name of environment variable>` always being preceded by a dollar sign `$`

because we can 

* test out if we can run these lines in python command line running in a bash terminal in a docker container
```
import subprocess

connection_id = "spark-conn"
connection_type = "spark"
host = "spark://spark-master"
port = "7077"
cmd = [
    "airflow",
    "connections",
    "add",
    connection_id,
    "--conn-host",
    host,
    "--conn-type",
    connection_type,
    "--conn-port",
    port,
]

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print(f"Successfully added {connection_id} connection")
else:
    print(f"Failed to add {connection_id} connection: {result.stderr}")
```

In this case we entered the docker container and used the containers bash terminal. We accessed the python cli and then ran a subprocess command
```
Type "help", "copyright", "credits" or "license" for more information.
>>> import subprocess
>>>
>>> cmd = ["airflow", "connections", "add", "my_spark_conn", "--conn-host", "spark://spark-master", "--conn-type", "spar
k", "--conn-port", "7077"]
>>> result = subprocess.run(cmd, capture_output=True, text=True)
>>> result.returncode
0
>>> # the command was successfully ran if the return code is 0 and otherwise if not
>>>
```

* there is no logs inside the webserver the reason why this is is because you turned off the logs in the volumes of the x-airflow-common service

* next thing is to figure out why the transform_forex_data task still fails even when the connection is added

* now because you turned off `logs` in the first place when you first created the `docker-compose` file and ran `docker compose up` the `logs` was never created and only the root user created the `config`, `dags`, `plugins`, and `include` folders excluding the `logs` folder, and when we uncomment the `logs` line in the `docker-compose` file we see that if we run `docker compose up` the `logs` file is not created by the root user anymore and requires certain persmissions now. This is why upon pulling of the `docker-compose.yaml` file from airflow right then adn there we shouldn't comment out `logs`
- Thank you this worked for me. If you don't set AIFLOW_UID, all files will be created as root user which causes permission issues. 
- workaround could be generating a `docker-compose.yaml` file again by pulling it from airflow `curl -LfO "https://airflow.apache.org/docs/apache-airflow/2.10.5/docker-compose.yaml"`. This problem has been solved

* when we enter the spark container and run the printenv command we get the ff:
```
(base) C:\Users\LARRY\Documents\Scripts\data-pipeline>docker ps
CONTAINER ID   IMAGE                             COMMAND                  CREATED              STATUS
          PORTS                                            NAMES
bcd926089ec1   data-pipeline-airflow-scheduler   "/usr/bin/dumb-init …"   About a minute ago   Up 46 seconds (health: starting)   8080/tcp                                         data-pipeline-airflow-scheduler-1
1ecb15e44536   data-pipeline-airflow-triggerer   "/usr/bin/dumb-init …"   About a minute ago   Up 46 seconds (health: starting)   8080/tcp                                         data-pipeline-airflow-triggerer-1
cd7cbb9d282b   data-pipeline-airflow-webserver   "/usr/bin/dumb-init …"   About a minute ago   Up 46 seconds (health: starting)   0.0.0.0:8080->8080/tcp                           data-pipeline-airflow-webserver-1
255ee184d425   bitnami/spark:latest              "/opt/bitnami/script…"   About a minute ago   Up About a minute                                                                   data-pipeline-spark-worker-1
29d198cc842b   postgres:13                       "docker-entrypoint.s…"   About a minute ago   Up About a minute (healthy)        5432/tcp                                         data-pipeline-postgres-1
ba23338662f3   bitnami/spark:latest              "/opt/bitnami/script…"   About a minute ago   Up About a minute                  0.0.0.0:7077->7077/tcp, 0.0.0.0:8081->8081/tcp   data-pipeline-spark-master-1

(base) C:\Users\LARRY\Documents\Scripts\data-pipeline>docker exec -it ba23338662f3 bash
I have no name!@ba23338662f3:/opt/bitnami/spark$ printenv
SPARK_SSL_ENABLED=no
NSS_WRAPPER_GROUP=/opt/bitnami/spark/tmp/nss_group
HOSTNAME=ba23338662f3
JAVA_HOME=/opt/bitnami/java
SPARK_MASTER_WEBUI_PORT=8081
NSS_WRAPPER_PASSWD=/opt/bitnami/spark/tmp/nss_passwd
SPARK_RPC_ENCRYPTION_ENABLED=no
PWD=/opt/bitnami/spark
OS_FLAVOUR=debian-12
LIBNSS_WRAPPER_PATH=/opt/bitnami/common/lib/libnss_wrapper.so
SPARK_RPC_AUTHENTICATION_ENABLED=no
HOME=/
SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
PYTHONPATH=/opt/bitnami/spark/python/:
TERM=xterm
SPARK_USER=spark
SPARK_MODE=master
SHLVL=1
SPARK_HOME=/opt/bitnami/spark
BITNAMI_APP_NAME=spark
LD_LIBRARY_PATH=/opt/bitnami/python/lib:/opt/bitnami/spark/venv/lib/python3.12/site-packages/numpy.libs:
APP_VERSION=3.5.5
OS_NAME=linux
PATH=/opt/bitnami/python/bin:/opt/bitnami/java/bin:/opt/bitnami/spark/bin:/opt/bitnami/spark/sbin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
OS_ARCH=amd64
_=/usr/bin/printenv
I have no name!@ba23338662f3:/opt/bitnami/spark$
```

* test if adding an s3 connection via bash in container will work e.g. `airflow connections add my_s3_conn --conn-type aws --conn-extra '{"aws_access_key_id": "<aws access key id>", "aws_secret_access_key": "<aws secret access key>", "region_name": "us-east-2"}'` and `airflow connections add my_spark_conn --conn-type spark --conn-port 7077 --conn-host spark://spark-master`. So before using Connections object and adding an aws connection in the airflow_settings.yaml didn't work and always resulted in airflow nto being able to retrieve credentials for some reason even if it was provided. 

* Now i have to fix the 
```
[2025-03-03, 08:53:24 UTC] {logging_mixin.py:190} INFO - Error creating bucket: An error occurred OperationAborted) when calling the CreateBucket operation: A conflicting conditional operation is currently in progress against this resource. Please try again.
[2025-03-03, 08:53:24 UTC] {taskinstance.py:3313} ERROR - Task failed with exception
Traceback (most recent call last):
  File "/home/airflow/.local/lib/python3.12/site-packages/airflow/models/taskinstance.py", line 768, in _execute_task
    result = _execute_callable(context=context, **execute_callable_kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/airflow/.local/lib/python3.12/site-packages/airflow/models/taskinstance.py", line 734, in _execute_callable
    return ExecutionCallableRunner(
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/airflow/.local/lib/python3.12/site-packages/airflow/utils/operator_helpers.py", line 252, in run
    return self.func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/airflow/.local/lib/python3.12/site-packages/airflow/models/baseoperator.py", line 424, in wrapper
    return func(self, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/airflow/.local/lib/python3.12/site-packages/airflow/operators/python.py", line 238, in execute
    return_value = self.execute_callable()
                   ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/airflow/.local/lib/python3.12/site-packages/airflow/operators/python.py", line 256, in execute_callable
    return runner.run(*self.op_args, **self.op_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/airflow/.local/lib/python3.12/site-packages/airflow/utils/operator_helpers.py", line 252, in run
    return self.func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/airflow/dags/operators/create_s3_bucket.py", line 8, in create_s3_bucket
    s3_hook.create_bucket(bucket_name=bucket_name, region_name=kwargs.get('region'))  # Region is important!
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/airflow/.local/lib/python3.12/site-packages/airflow/providers/amazon/aws/hooks/s3.py", line 126, in wrapper
    return func(*bound_args.args, **bound_args.kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/airflow/.local/lib/python3.12/site-packages/airflow/providers/amazon/aws/hooks/s3.py", line 360, in create_bucket
    self.get_conn().create_bucket(
  File "/home/airflow/.local/lib/python3.12/site-packages/botocore/client.py", line 569, in _api_call
    return self._make_api_call(operation_name, kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/airflow/.local/lib/python3.12/site-packages/botocore/client.py", line 1023, in _make_api_call
    raise error_class(parsed_response, operation_name)
botocore.exceptions.ClientError: An error occurred (OperationAborted) when calling the CreateBucket operation: A conflicting conditional operation is currently in progress against this resource. Please try again.
```
error but this is likely due to the process already being done and when the dag retried when the prior dag was finished implying hte bucket creation task was also finished then the creation of the bucket or rather retrieval of the bucket was successful which can be seen in the second attempts log

```
[2025-03-03, 08:55:25 UTC] {local_task_job_runner.py:123} ▶ Pre task execution logs
[2025-03-03, 08:55:25 UTC] {base.py:84} INFO - Retrieving connection 'my_s3_conn'
[2025-03-03, 08:55:25 UTC] {connection_wrapper.py:328} INFO - AWS Connection (conn_id='my_s3_conn', conn_type='aws') credentials retrieved from extra.
[2025-03-03, 08:55:28 UTC] {logging_mixin.py:190} INFO - Bucket 'usd-php-ml-pipeline-bucket' already exists. Skipping creation.
[2025-03-03, 08:55:28 UTC] {python.py:240} INFO - Done. Returned value was: None
[2025-03-03, 08:55:28 UTC] {taskinstance.py:341} ▶ Post task execution logs
```