from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def create_s3_bucket(**kwargs):
    s3_hook = S3Hook(aws_conn_id="my_s3_conn")  # Use your connection ID
    bucket_name = kwargs.get('bucket_name')  # Replace with a unique name

    try:
        s3_hook.create_bucket(bucket_name=bucket_name, region_name=kwargs.get('region'))  # Region is important!
        print(f"Bucket '{bucket_name}' created successfully.")
    except Exception as e:
        if "BucketAlreadyExists" in str(e) or "BucketAlreadyOwnedByYou" in str(e):
            print(f"Bucket '{bucket_name}' already exists. Skipping creation.")
        else:
            print(f"Error creating bucket: {e}")
            raise  # Re-raise the exception to fail the task