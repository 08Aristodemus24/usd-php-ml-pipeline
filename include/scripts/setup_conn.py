import subprocess
import os

def add_airflow_connection(**kwargs):
    conn_id = kwargs.get("conn_id")
    cmd = ["airflow", "connections", "add", conn_id]
    for key, value in kwargs.items():
        if not "conn_id" in key:
            key = key.replace("_", "-")

            if "conn_extra" in key:
                value = str(value).replace("'", '"')
            
            # append connection key and its corresponding value
            cmd.append(f"--{key}")
            cmd.append(value)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully added {conn_id} connection")
    else:
        print(f"Failed to add {conn_id} connection: {result.stderr}")

def add_connections(connections: dict):
    for conn_name, conn_kwargs in connections.items():
        print(f"adding {conn_name} connection...")
        add_airflow_connection(**conn_kwargs)

if __name__ == "__main__":
    connections = {
        "spark_conn": {
            "conn_id": "my_spark_conn", 
            "conn_type": "spark", 
            "conn_port": "7077", 
            "conn_host": "spark://spark-master"
        },
        "s3_conn": {
            "conn_id": "my_s3_conn", 
            "conn_type": "aws", 
            "conn_extra": {
                "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID"), 
                "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
                "region_name": os.environ.get("AWS_REGION_NAME")
            }
        }
    }
    add_connections(connections)