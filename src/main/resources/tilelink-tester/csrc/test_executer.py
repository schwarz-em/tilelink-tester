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
parser.add_argument('-dir_name', action = "store_true", help = "Wee", default = "" )
parser.add_argument('-r', action = "store_true", help = "Flag", default = False )


#EDIT THIS IF YOU WANT TO EDIT YOUR MAKE COMMAND
make_command = r'''make MODEL=TLTestHarness MODEL_PACKAGE=ddr CONFIG=DDRTLTConfig CONFIG_PACKAGE=ddr BINARY=$RISCV/riscv64-unknown-elf/share/riscv-tests/isa/rv64ui-p-simple run-binary TOP=TLDDRTester CLOCK_PERIOD=5.0 EXTRA_SIM_FLAGS='+tltestfile=[FILEPATH]' > [COUNTER]'''
# EDIT THIS WITH THE APPROPRIATE VCS DIRECTORY
sims_directory = "/scratch/asun/chipyard/sims/vcs"
# EDIT THIS WITH THE APPROPRIATE .OUT FILE DIRECTORY
out_directory = "/scratch/asun/chipyard/sims/vcs/output/ddr.TLTestHarness.DDRTLTConfig/rv64ui-p-simple.out"
# EDIT THIS WITH THE LIST OF TESTS YOU WANT TO RUN
#test_list = [avg_cycle_time]

def run_folder(folder_path, name):
    source_dir = None
    counter = 0
    
    try:
        source_dir = Path(folder_path)
    except:
        print("Error: Check the path to your directory")


    if name == '':
        #Captures the current time of testing and dumps all log files into this directory
        datetime_str = str(datetime.datetime.now()).replace(" ", "")
        log_file_directory = (sims_directory + "/" + datetime_str)
    else:
        log_file_directory = (sims_directory + "/" + name)
    create_folder(log_file_directory)

    dump_path = sims_directory + "/" + datetime_str + "/" + "Output"

    #can handle nested folders
    root_dir = Path(source_dir)
    for file_path in root_dir.rglob("*"):  
       if file_path.is_file():  
            print(file_path)
            counter = counter + 1
            final_command = (make_command.replace("[FILEPATH]", str(file_path))).replace("[COUNTER]", datetime_str +"/test_" + str(counter))
            status = subprocess.run(final_command, cwd=sims_directory, text = True, capture_output=True, shell=True)
            scrape_data(dump_path, counter)
            print("Return code_" + str(counter), status.returncode)
            print("\n")
            print("Output_" + str(counter), status.stdout)
    
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

def validate_tests(file_path):
    addresses = {}
    counter = 0
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
    print("creating folder at")
    print(folder_path)
    try:
        os.makedirs(folder_path)
    except:
        pass

def run_diagnostics(file_name, dir_name):
    test_number = 5
    folder_path = str(Path.cwd()) + "/test_files/" + "Regression_Test_" + str(file_name)
    create_folder(folder_path)
    tests = ["single_address", "strided_random", "interleaved", "preload_random"]

    for test in tests:
        for stride in range(2,5):
            for request_factor in range (1,5):
                test_generator.generate(folder_path, test_number, "Regression", test, request_factor * 100, 16**stride)
    
    print(folder_path)
    #fix the run folder so that it can run nested folders as well
    run_folder(folder_path,dir_name)

    return

def main():
    args = parser.parse_args()
    folder_path = ("%s" % args.file_name)
    if (args.csv):
        find_instances(folder_path)
    elif (args.validate):
        validate_tests(folder_path)
    elif (args.r):
        run_diagnostics(args.file_name, args.dir_name)
    else:
        run_folder(folder_path, args.dir_name)

if __name__ == "__main__":
    main()
