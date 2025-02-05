import random
import argparse
from pathlib import Path
import subprocess
import os
import sys
import datetime


parser = argparse.ArgumentParser()
parser.add_argument('file_name', help="File Name")
args = parser.parse_args()


#EDIT THIS IF YOU WANT TO EDIT YOUR MAKE COMMAND
make_command = r'''make MODEL=TLTestHarness MODEL_PACKAGE=ddr CONFIG=DDRTLTConfig CONFIG_PACKAGE=ddr BINARY=$RISCV/riscv64-unknown-elf/share/riscv-tests/isa/rv64ui-p-simple run-binary TOP=TLDDRTester CLOCK_PERIOD=5.0 EXTRA_SIM_FLAGS='+tltestfile=[FILEPATH]' > [COUNTER]'''
# EDIT THIS WITH THE APPROPRIATE VCS DIRECTORY
sims_directory = "/scratch/asun/chipyard/sims/vcs"
# EDIT THIS WITH THE APPROPRIATE .OUT FILE DIRECTORY
out_directory = "/scratch/asun/chipyard/sims/vcs/output/ddr.TLTestHarness.DDRTLTConfig/rv64ui-p-simple.out"
# EDIT THIS WITH THE LIST OF TESTS YOU WANT TO RUN
#test_list = [avg_cycle_time]

def run_folder(folder_path):
    source_dir = None
    counter = 0
    
    try:
        source_dir = Path(folder_path)
    except:
        print("Error: Check the path to your directory")

    files = source_dir.iterdir()

    #Captures the current time of testing and dumps all log files into this directory
    datetime_str = str(datetime.datetime.now()).replace(" ", "")
    log_file_directory = (sims_directory + "/" + datetime_str)
    create_folder(sims_directory + "/" + datetime_str)

    for f in files:
        print(f)
        counter = counter + 1
        final_command = (make_command.replace("[FILEPATH]", str(f))).replace("[COUNTER]", datetime_str +"/test_" + str(counter))
        scrape_data(sims_directory + "/" + datetime_str + "/" + "Output", counter)
        status = subprocess.run(final_command, cwd=sims_directory, text = True, capture_output=True, shell=True)
        print("Return code_" + str(counter), status.returncode)
        print("\n")
        print("Output_" + str(counter), status.stdout)
    
def scrape_data(dump_path, test_num):
    print("Scraping Data from .Out File")
    with open(out_directory, 'r') as source:
        contents = source.read()
    
    with open(dump_path, 'a') as dump_file:
        dump_file.write("******************************************************\n")
        dump_file.write(f"TEST # {test_num}\n")
        dump_file.write("******************************************************\n\n\n")
        dump_file.write(contents)
        dump_file.write("\n\n\n")
        dump_file.flush()

def find_instances(dump_path, parameter_name):
    with open(dump_path, 'r') as dump_file:
        pattern = fr"{parameter_name} (\d+)"
        matches = re.findall(pattern, dump_file.read())
        numbers = [int(match) for match in matches]    
    return (numbers)

def avg_cycle_time(dump_path):
    cycle_times = find_instances(dump_path, "TEST TOTAL CYCLE TIME")
    return (sum(cycle_times) / len(cycle_times))

def create_folder(folder_path):
    print("creating folder at")
    print(folder_path)
    try:
        os.makedirs(folder_path)
    except:
        pass
    
def main():  
    folder_path = ("%s" % args.file_name)
    run_folder(folder_path)

if __name__ == "__main__":
    main()
