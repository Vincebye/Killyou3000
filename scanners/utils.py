from datetime import datetime, timedelta
from urllib.parse import urlparse
import os
def read_data_from_file(file_path):
    with open(file_path, "r") as file:
        datas = file.read().splitlines()
    return datas
def generate_filename(target, ftype):
    now = datetime.now()
    year = now.year
    month = now.month
    filename = f"{target}_{ftype}_{year}_{month:02d}.txt"
    return filename

def check_and_execute(target, execute_function):
    now = datetime.now()

    files_with_target_prefix = [
        filename for filename in os.listdir() if filename.startswith(target)]

    if files_with_target_prefix:
        for filename in files_with_target_prefix:
            if filename.endswith(".txt"):
                year_month = filename[:-4].split("_")[2:4]
                print(year_month)
                file_creation_time = datetime.strptime(
                    year_month[0]+'_'+year_month[1], "%Y_%m")
                time_difference = now - file_creation_time

                if time_difference <= timedelta(days=30):
                    print(f"File '{filename}' is recent. Skipping function A.")
                else:
                    print(
                        f"File '{filename}' is older. Deleting and executing function A.")
                    os.remove(filename)
                    execute_function()
    else:
        execute_function()

def parse_target_from_url(url):
    parsed_url = urlparse(url)
    target = parsed_url.netloc
    if target.startswith("www."):
        target = target[4:]  # 去除前面的 "www."
    return target