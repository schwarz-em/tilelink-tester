import random
import argparse
from pathlib import Path
import subprocess
import os
import sys
import datetime
import csv
import test_generator

parser = argparse.ArgumentParser()
parser.add_argument('file_name', help="File Name")
parser.add_argument('-c', '--csv', action = "store_true", help = "Flag to convert to CSV", default = False)
parser.add_argument('-v', '--validate', action = "store_true", help = "Flag to Validate a set of Test Files", default = False)
parser.add_argument('-dir_name', action = "store", help = "Wee", default = "" )

current_directory = os.getcwd()
cwd_index= current_directory.index("tools/tilelink-tester")
sims_directory = current_directory[:cwd_index] + "sims/vcs"
out_directory = current_directory[:cwd_index] + "sims/vcs/output/ddr.TLTestHarness.DDRTLTConfig/rv64ui-p-simple.out"

print("Running VCS in", sims_directory)
print("Reading Simulation Output from", out_directory)
#EDIT THIS IF YOU WANT TO EDIT YOUR MAKE COMMAND
make_command = r'''make MODEL=TLTestHarness MODEL_PACKAGE=ddr CONFIG=DDRTLTConfig CONFIG_PACKAGE=ddr BINARY=$RISCV/riscv64-unknown-elf/share/riscv-tests/isa/rv64ui-p-simple run-binary TOP=TLDDRTester CLOCK_PERIOD=5.0 EXTRA_SIM_FLAGS='+tltestfile=[FILEPATH]' > [COUNTER]'''
# EDIT THIS WITH THE LIST OF TESTS YOU WANT TO RUN
#test_list = [avg_cycle_time]

def run_folder(folder_path, name):
    source_dir = None
    counter = 0
    
    print("\n TEST FOLDER PATH: ", folder_path)
    try:
        source_dir = Path(folder_path)
    except:
        print("Error: Check the path to your directory")
    directory_name = name
    datetime_str = str(datetime.datetime.now()).replace(" ", "")
    if name == '':
        directory_name = datetime_str
        #Captures the current time of testing and dumps all log files into this directory
    log_file_directory = (sims_directory + "/" + directory_name)

    create_folder(log_file_directory)
    dump_path = log_file_directory + "/" + "Output"

    #can handle nested folders
    root_dir = Path(source_dir)
    for file_path in root_dir.rglob("*"):  
       if file_path.is_file():  
            counter = counter + 1
            file_name = directory_name +"/" + (str(file_path).split("/"))[-1]
            final_command = (make_command.replace("[FILEPATH]", str(file_path))).replace("[COUNTER]", (file_name))
            print("\n RUNNING COMMAND...",final_command)
            status = subprocess.run(final_command, cwd=sims_directory, text = True, capture_output=True, shell=True)
            
            scrape_data(dump_path, counter)
            print("Return code_" + str(counter), status.returncode)
            print("\n")

    scrape_diagnostics(log_file_directory)
    
    return log_file_directory
    
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

def only_numerics(seq):
    return list(filter(type(seq).isdigit, seq))

def validate_tests(folder_path):
    addresses = {}
    counter = 0

    try:
        source_dir = Path(folder_path)
    except:
        print("Error: Check the path to your directory")

    root_dir = Path(source_dir)
    for file_path in root_dir.rglob("*"): 
        counter = 0 
        if file_path.is_file():
            with open (file_path, 'r') as test_file:
                for row in test_file:
                    if (counter == 0) : 
                        counter += 1
                        continue
                    request = (row.replace(" ","")).split(',')

                    if (int(request[0])):
                        addresses[request[1]] = request[2]
                    elif (request[2] != addresses.get(request[1])):
                        print(f"ERROR AT LINE {counter}")
                        print(f" REQUESTED {request[2]} at {request[0]} but got {addresses.get(request[1])}")
                    counter += 1
    

def find_instances(dump_path):
    #file reading
    source_dir = None
    
    try:
        source_dir = Path(dump_path)
    except:
        print("Check your Path")
    
    out_file_iter = source_dir.iterdir()

    #set the directory for the output
    csv_path_out = dump_path
    #set directory for output file
    f = dump_path + "/" + "Output"

    #identify test number
    test_id = str(f).rsplit("/", 1) [1]
    #create a new csv
    csv_file_path = dump_path + "/" + test_id + ".csv"
    #iterate over each line
    outfile = open(f,'r')
    csvfile = open(csv_file_path, 'w')

    lines = outfile.readlines()
    split_list = [item.split(" ") for item in lines]
    cleaned_list = [[y for y in x if y != ''] for x in split_list if ">" in x or "PASSED" in x]

    #iterate over each list, find each indices of >, find the one before
    fields = []
    rows = []
    for row in cleaned_list:
        inner_row = []

        if ("PASSED" in row):
            inner_row.extend([0]*len(fields))
            inner_row.append(row[5])
        else:
            indices = [i for i in range(len(row)) if row[i] == '>']
            for index in indices:
                if(type(row[index-1]).isdigit) and row[index-1] not in fields[:index]:
                    fields.append(row[index-1])
                inner_row.append(row[index+1])
        rows.append(inner_row)
    
    fields.append("Total Cycle Time")

    # creating a csv writer object
    csvwriter = csv.writer(csvfile)
    # writing the fields
    csvwriter.writerow(fields)
    # writing the data rows
    csvwriter.writerows(rows)
    outfile.close()
    csvfile.close()
    return 

def avg_cycle_time(dump_path):
    cycle_times = find_instances(dump_path, "TEST TOTAL CYCLE TIME")
    return (sum(cycle_times) / len(cycle_times))

def create_folder(folder_path):
    print("\n CREATING FOLDER AT...", folder_path)
    try:
        os.makedirs(folder_path)
    except:
        pass


def scrape_diagnostics(folder_path):
    cols = ["Test Name", "Pass/Fail", "Error", "Total Cycle Time"]
    rows = []

    try:
        source_dir = Path(folder_path)
    except:
        print("Error: Check the path to your directory")

    #can handle nested folders
    root_dir = Path(source_dir)
    for file_path in root_dir.rglob("*"):  
        test_name_temp = ""
        error_temp = "NA"
        pass_temp = 0
        total_cycle_temp = ""
        lines = []
        result = []
        if file_path.is_file():
            test_name_temp = str(file_path).split("/")[-1]
            if (test_name_temp != "Output" and test_name_temp !="diagnostics.csv"):
                with open (file_path, 'r') as out_file:
                    lines = out_file.read().splitlines() # Read all lines at once
                result = [(line.lstrip().split(maxsplit=1) + [""])[:1] for line in lines]    
                if ['An'] in result:
                    error_temp = (lines[result.index(['An'])])
                elif ['Error:'] in result:
                    error_temp =(lines[result.index(['Error:'])])
                else:
                    pass_temp = 1
                rows.append([test_name_temp, str(pass_temp), error_temp, total_cycle_temp])
    
    csv_file_path = folder_path + "/" + "diagnostics.csv"
    csvfile = open(csv_file_path, 'w')
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(cols)
    csvwriter.writerows(rows)
    csvfile.close()

    return csv_file_path      

def main():
    args = parser.parse_args()
    folder_path = ("%s" % args.file_name)

    if (args.csv):
        find_instances(folder_path)
    elif (args.validate):
        validate_tests(folder_path)
    else:
        run_folder(folder_path, args.dir_name)

if __name__ == "__main__":
    main()
