import os

def test_pull_forex_data(formatter, save_path, ti):
    # # mimics replacement of file path when returned from pull_forex_data task
    # # relative file path
    # new_file_path = "./include/data/usd_php_forex_4hour.csv"

    # absolute file path
    new_file_path = os.path.join(save_path, "usd_php_forex_4hour.csv")
    ti.xcom_push(key="new_file_path", value=new_file_path)

    # get api key
    # api_key = ti.xcom_pull(key="api_key", task_ids="get_env_vars")

    # print(f"api_key: {api_key}")
    print(f"save_path: {save_path}")