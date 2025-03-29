from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def move_raw_forex(ti, **kwargs):
    s3_hook = S3Hook(aws_conn_id="my_s3_conn")  # Use your connection ID
    bucket_name = kwargs.get('bucket_name')  # Replace with a unique name
    file_path = kwargs.get('filepath')
    dest = kwargs.get('destination')
    print(f"container local file path: {file_path}")
    print(f"s3 file path: {dest}")

    # push destination file path as xcom
    s3_raw_uri = f"s3a://{bucket_name}/{dest}"
    print(f"s3 raw uri: {s3_raw_uri}")
    ti.xcom_push(key="s3_raw_uri", value=s3_raw_uri)

    try:
        # Region is important!
        s3_hook.load_file(file_path, dest, bucket_name=bucket_name, replace=True)  
        print(f"Bucket '{bucket_name}' created successfully.")
    except Exception as e:
        print(f"Error {e} occured")