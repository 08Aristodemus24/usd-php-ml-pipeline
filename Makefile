# start containers in detached mode so that after starting
# it doesn't leave containers running in the terminal so that
# subsequent commands can run such as do-sleep and setup-conn
start-containers:
	docker compose build && docker compose up --detach

# timeout for 30 seconds to make sure container
do-sleep:
	timeout 30

# once containers are started and waited for 30 seconds the nex command
# in sequence to run is to run a script inside a running airflow container
# that will setup our airflow connections in the container from our 
# local machine  
setup-conn:
	docker exec usd-php-ml-pipeline-airflow-webserver-1 python /opt/airflow/include/scripts/setup_conn.py

up: start-containers do-sleep setup-conn

down:
	docker compose down

sh:
	docker exec -it usd-php-ml-pipeline-airflow-webserver-1 bash

restart: down up
