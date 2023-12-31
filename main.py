import argparse

import subprocess
import socket
import os
from datetime import datetime, timedelta
import re
import asyncio
import aiohttp
from jinja2 import Environment, FileSystemLoader

from scanners.subdomain_scaner import Subdomain
import requests
port_scan_binary_path = "E:\\pentest\\RustScan\\target\\release\\rustscan.exe"
# 正则表达式模式匹配IP地址
ip_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
cdn_keywords = ['cloudflare','akamai','fastly','ali','tencent'] 
def process_domain(domain):
    if not domain.startswith('http://') and not domain.startswith('https://'):
        domain = 'http://' + domain
    return domain

def run_rustscan(target,output_file):
    command = [port_scan_binary_path, "-a", target, "--scan-order", "Random"]
    result = subprocess.run(
        command, capture_output=True, text=True, shell=True)
    output = result.stdout.strip().split("\n")
    write_to_file(output,output_file,'w')
    print(output)
    return output

def run_rustscan_onebyone(targets,output_file):
    for target in targets:
        command = [port_scan_binary_path, "-a", target, "--scan-order", "Random"]
        result = subprocess.run(
            command, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            print(f"Failed to run rustscan for target {target}: {result.stderr}")
            continue
        if result.stdout is None or result.stdout == "":
            print(f"Failed to run rustscan for target {target}: no output")
            continue
        output = result.stdout.strip().split("\n")
        write_to_file(output,output_file,'w')
        print(output)
    return output




async def fetch_status_code(session,url):
    url=process_domain(url)
    try:
        async with session.get(url,headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}) as response:
            return url, response.status
    except Exception as e:
        return url, str(e)



def check_file_exist(file_path):
    if os.path.exists(file_path):
        return True
    else:
        return False
def write_to_file(datas, file_path,mode='w'):
    with open(file_path, mode) as file:
        for ip in datas:
            file.write(ip + "\n")
def extract_ip(data):
    ip_addresses = re.findall(ip_pattern, data.lower())
    unique_ip_addresses = list(set(ip_addresses))
    return unique_ip_addresses

def analyse_ping_result_to_no_cdn_ip(ping_result,out_file_path):
    ip_list = []

    cdns=[]
    cdn_file_path = out_file_path.replace('ip','cdn')
    for line in ping_result:
        ips=[]
        ips=extract_ip(line)
        flag=False
        for cdn_keyword in cdn_keywords:
            if cdn_keyword in line.lower():
                flag=True
                cdns.extend(ips)
                break
        if '超时' in line:
            flag=True
        if not flag:
            ip_list.extend(ips)
    cdns=list(set(cdns))
    ips=list(set(ip_list))    
    write_to_file(cdns,cdn_file_path)
    write_to_file(ips,out_file_path)
    return ip_list

async def ping_domain(domain):
    try:
        ping_output = await asyncio.create_subprocess_shell(f"ping {domain}", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await ping_output.communicate()
        return stdout.decode('gbk', errors='replace')
    except asyncio.CancelledError:
        ping_output.kill()
        await ping_output.communicate()
        raise
    except Exception as e:
        return f"Failed to ping domain {domain}: {e}"
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


async def main():
    # 1. Parse arguments
    parser = argparse.ArgumentParser(
        description="Parse URL and extract target")
    parser.add_argument("-u", "--url", type=str,
                        required=True, help="URL to be parsed")

    args = parser.parse_args()
    url = args.url
    #Subdomain().run(url)
    sub=Subdomain()
    sub.monitor(url)
    # 3. Get the domains StateCode
#     status_codes = {}

#     async with aiohttp.ClientSession() as session:
#         tasks = [fetch_status_code(session, subdomain) for subdomain in subdomains]
#         results = await asyncio.gather(*tasks)

#         for url, status_code in results:
#             status_codes[url] = status_code
#     # for url in subdomains:
#     #     url, status_code = fetch_status_code(url)
#     #     status_codes[url] = status_code

#     env = Environment(loader=FileSystemLoader('.'))
#     template = env.get_template('report_template.html')

#     html_content = template.render(status_codes=status_codes)
#  # 将HTML内容保存到文件
#     with open('report.html', 'w') as file:
#         file.write(html_content)

#     print("报告已生成：report.html")
#     for url, status_code in status_codes.items():
#         print(f"{url}: {status_code}")
    # 4. Get unique IPs
    # out_ip_file = generate_filename(target, 'ip')

    # if not check_file_exist(out_ip_file):
    #     tasks = [ping_domain(domain) for domain in subdomains]
    #     results = await asyncio.gather(*tasks)
    # else:
    #     results = read_data_from_file(out_ip_file)
    # check_and_execute(out_ip_file, lambda: analyse_ping_result_to_no_cdn_ip(
    #     results, out_ip_file))

    # unique_ips = read_data_from_file(out_ip_file)
    #target_ips = ",".join(unique_ips)

    # out_port_file = generate_filename(target, 'port')

    # check_and_execute(out_port_file, lambda: run_rustscan_onebyone(unique_ips,out_port_file))


if __name__ == "__main__":
    asyncio.run(main())
