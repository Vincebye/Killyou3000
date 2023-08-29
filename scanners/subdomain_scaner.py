from .utils import parse_target_from_url,generate_filename,check_and_execute,read_data_from_file
class Subdomain:
    def __init__(self):
        pass
    def run_subfinder(self,target, output_file):
        command = ["subfinder", "-d", target, "-o", output_file]
        subprocess.run(command, capture_output=True, shell=True)
    @classmethod
    def run(self,url):
        target = parse_target_from_url(url)
        print("Extracted target:", target)
        # 2. Check need to run_sunfinder
        output_file = generate_filename(target, 'subdomain')
        check_and_execute(output_file, lambda: run_subfinder(target, output_file))
        subdomains = read_data_from_file(output_file)
        print("Subdomains found:")
    @classmethod
    def monitor(self,url):
        
        pass
    