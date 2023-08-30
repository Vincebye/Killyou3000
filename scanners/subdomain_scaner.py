from .utils import parse_target_from_url,generate_filename,check_and_execute,read_data_from_file
from .monitor import send_email
from datetime import datetime, timedelta
from .logger import setup_logger
import glob
import subprocess
class Subdomain:
    def __init__(self):
        pass
    
    def run_subfinder(self,target, output_file):
        command = ["subfinder", "-d", target, "-o", output_file]
        subprocess.run(command, capture_output=True, shell=True)
    
    def check_format_file_exists(self,url):
        target = parse_target_from_url(url)
        current_date=datetime.now().strftime("%Y_%m")
        file_pattern=f"{target}_subdomain*.txt"
        files=glob.glob(file_pattern)
        if files:
            files.sort(reverse=True)
            newest_file=files[0]
            with open(newest_file,'r') as file:
                data=file.readlines()
            return data
        else:
            return None
    def find_different_elements(self,listA, listB):
        setA = set(listA)
        setB = set(listB)
        diff_A = setA - setB
        diff_B = setB - setA
        different_elements = diff_A.union(diff_B)
        return different_elements
    def write_to_log(self,message,log_file):
        with open(log_file,'a') as file:
            file.write(message+'\n')
    def init_monitor(self):
        config.read("config.ini")
        sender_email = config.get('mail', 'sender_email')
        sender_password = config.get('mail', 'sender_password')
        receive_email = config.get('mail', 'receive_email')

        return sender_email,sender_password,receive_email
    
        
    
    def run(self,url):
        target = parse_target_from_url(url)
        print("Extracted target:", target)
        # 2. Check need to run_sunfinder
        output_file = generate_filename(target, 'subdomain')
        check_and_execute(output_file, lambda: self.run_subfinder(target, output_file))
        subdomains = read_data_from_file(output_file)
        print("Subdomains found:")
    def monitor(self,url):
        log_file = 'log.txt'

        logger = setup_logger(log_file)

        current_data=self.check_format_file_exists(url)
        if current_data is None:
            self.run(url)
            current_data=self.check_format_file_exists(url)
        self.run(url)
        new_data=self.check_format_file_exists(url)
        if len(new_data)>len(current_data):
            diff_data=self.find_different_elements(current_data,new_data)
            subject='New subdomain'
            message=' '.join(diff_data)
            s_mail,s_pass,r_mail=send_email(sender_email, sender_password, receive_email, subject, message)

        text=f"{url}-{len(new_data)}-{len(current_data)}"
        logger.info(text)
            
            
        

        
    