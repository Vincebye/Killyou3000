import argparse
from urllib.parse import urlparse
import subprocess
import socket
import os
from datetime import datetime, timedelta
import re

port_scan_binary_path = "E:\\pentest\\RustScan\\target\\release\\rustscan.exe"
# 正则表达式模式匹配IP地址
ip_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"


def generate_filename(target, ftype):
    now = datetime.now()
    year = now.year
    month = now.month
    filename = f"{target}_{ftype}_{year}_{month:02d}.txt"
    return filename


def parse_target_from_url(url):
    parsed_url = urlparse(url)
    target = parsed_url.netloc
    if target.startswith("www."):
        target = target[4:]  # 去除前面的 "www."
    return target


def run_subfinder(target, output_file):
    command = ["subfinder", "-d", target, "-o", output_file]
    subprocess.run(command, capture_output=True, shell=True)


def run_rustscan(target):
    command = [port_scan_binary_path, "-a", target, "--scan-order", "Random"]
    result = subprocess.run(
        command, capture_output=True, text=True, shell=True)
    output = result.stdout.strip().split("\n")
    print(output)
    return output


def read_data_from_file(file_path):
    with open(file_path, "r") as file:
        datas = file.read().splitlines()
    return datas


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

def check_file_exist(file_path):
    if os.path.exists(file_path):
        return True
    else:
        return False
def write_to_file(datas, file_path,mode='w'):
    with open(file_path, mode) as file:
        for ip in datas:
            file.write(ip + "\n")

def get_check_cdn_ping_to_ip(domain_list, file_path):
    result=[]
    cdns=[]
    failed=[]
    cdn_keywords = ['cloudflare','akamai','fastly','ali','tencent']  # 要检查的关键词

    cdn_file=file_path.replace('ip','cdn')
    filed_file=file_path.replace('ip','failed')
    if check_file_exist(cdn_file):
        cdns=read_data_from_file(cdn_file)
    if check_file_exist(filed_file):
        failed=read_data_from_file(filed_file)
    else:
        for domain in domain_list:
            if len(cdns)%10==0:
                cdns=list(set(cdns))
                write_to_file(cdns,cdn_file)
            if len(failed)%10==0:
                failed=list(set(failed))
                write_to_file(failed,filed_file)
            if domain not in cdns and domain not in failed:
                try:
                    ping_output = subprocess.check_output(["ping", domain], universal_newlines=True)
                    flag=False
                    for cdn_keyword in cdn_keywords:
                        if cdn_keyword in ping_output.lower():
                            flag=True
                            print(f"Domain {domain} may be associated with a CDN.")
                            cdns.append(domain)
                            break
                    if not flag:
                        ip_addresses = re.findall(ip_pattern, ping_output.lower())
                        unique_ip_addresses = list(set(ip_addresses))
                        result.extend(unique_ip_addresses)
                        print(f"Domain {domain} doesn't seem to be associated with a CDN.")
                except subprocess.CalledProcessError:
                    failed.append(domain)
                    print(f"Failed to ping domain {domain}.")
    cdns=list(set(cdns))
    failed=list(set(failed))
    write_to_file(cdns,cdn_file)
    write_to_file(failed,filed_file)
    write_to_file(result, file_path)
    return result

#Giveup
def get_unique_ips(domain_list, file_path):
    ip_set = set()
    for domain in domain_list:
        try:
            ip_addresses = socket.getaddrinfo(domain, None)
            for addr_info in ip_addresses:
                ip = addr_info[4][0]
                ip_set.add(ip)
        except socket.gaierror:
            print(f"Could not resolve IP for domain: {domain}")
    unique_ips = list(ip_set)
    write_to_file(unique_ips, file_path)
    return unique_ips


def main():
    # 1. Parse arguments
    parser = argparse.ArgumentParser(
        description="Parse URL and extract target")
    parser.add_argument("-u", "--url", type=str,
                        required=True, help="URL to be parsed")

    args = parser.parse_args()
    url = args.url

    target = parse_target_from_url(url)
    print("Extracted target:", target)

    # 2. Check need to run_sunfinder
    output_file = generate_filename(target, 'subdomain')
    check_and_execute(output_file, lambda: run_subfinder(target, output_file))

    subdomains = read_data_from_file(output_file)

    print("Subdomains found:")
    # 3. Get unique IPs
    out_ip_file = generate_filename(target, 'ip')
    check_and_execute(out_ip_file, lambda: get_check_cdn_ping_to_ip(
        subdomains, out_ip_file))
    unique_ips = read_data_from_file(out_ip_file)
    # unique_ips = get_unique_ips(subdomains)

    write_to_file(unique_ips, out_ip_file)
    target_ips = ",".join(unique_ips)
    check_and_execute(out_ip_file, lambda: run_rustscan(target_ips))
    # run_rustscan(target_ips)


if __name__ == "__main__":
    main()
