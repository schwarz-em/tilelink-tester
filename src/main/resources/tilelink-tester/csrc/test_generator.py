import random
import argparse
from pathlib import Path
import subprocess
import os
import sys

#EDIT THIS IF YOU WANT TO EDIT YOUR MAKE COMMAND
make_command = r'''make MODEL=TLTestHarness MODEL_PACKAGE=ddr CONFIG=DDRTLTConfig CONFIG_PACKAGE=ddr BINARY=$RISCV/riscv64-unknown-elf/share/riscv-tests/isa/rv64ui-p-simple run-binary TOP=TLDDRTester CLOCK_PERIOD=5.0 EXTRA_SIM_FLAGS='+tltestfile=[FILEPATH]' > [COUNTER]'''
# EDIT THIS WITH THE APPROPRIATE VCS DIRECTORY
sims_directory = "/scratch/asun/chipyard/sims/vcs"

parser = argparse.ArgumentParser()
parser.add_argument('file_name', help="File Name")
parser.add_argument('-num_reqs', type=int, help="Number of requests per test", default = 0)
parser.add_argument('-type', type=str, help="Type of Test", default='random')
parser.add_argument('-num_tests', type = int, help = "number of tests", default = 1)
parser.add_argument('--run', action='store_true' , help = "run or just generate tests" )

args = parser.parse_args()

"""
example: python test_generator.py random_10_test1 10 random
"""

def main():  
    # If --option is not selected, we force the user to provide arg1 and arg2
    if not args.run:
        if not args.num_reqs or not args.num_tests or not args.type:
            print("Error: You are generating test files. Test name, Type and # of requests must be specified.")
            sys.exit(1)  
        else:
            print("Generating Test Files...")

    number = args.num_reqs

    testtype = args.type
    folder_path = ("test_files/%s_%d_%s" % (args.type, args.num_reqs, args.file_name))
    create_folder(folder_path)

    if not (args.run):
        for i in range (0, args.num_tests):
            filename = (folder_path + "/%s_%s" % (args.file_name, i))
            f = open(filename,'w')

            if testtype =='random':
                random_test(f, number)
            elif testtype == 'single_address':
                single_addr_test(f, number)
            f.close()
    else:
        folder_path = ("%s" % args.file_name)
        run_folder(folder_path)
            
def run_folder(folder_path):
    source_dir = None
    counter = 0
    
    try:
        source_dir = Path(folder_path)
    except:
        print("Error: Check the path to your directory")

    files = source_dir.iterdir()
    for f in files:
        counter = counter + 1
        final_command = (make_command.replace("[FILEPATH]", str(f))).replace("[COUNTER]", "test_" + str(counter))
        status = subprocess.run(final_command, cwd=sims_directory, text = True, capture_output=True, shell=True)
        print("Return code_" + str(counter), status.returncode)
        print("\n")
        print("Output_" + str(counter), status.stdout)

def single_addr_test(f,num_reqs):
    address= (0x100000000 + (0x0010 * random.randint(0,10)))
    num_reqs = num_reqs * 2
    f.write(f"{num_reqs}\n")  
    response_req = [1] * (num_reqs // 2) + [0] * (num_reqs // 2)
    hex_addresses = [f"0x{address:X}" for i in range(num_reqs //2)]
    decimal_outputs = [random.randint(1,100) for i in range(num_reqs //2)]  
    for i in range (num_reqs //2):
        f.write(", ".join(['1',str(hex_addresses[i]),str(decimal_outputs[i])]) + "\n")
        f.write(", ".join(['0',str(hex_addresses[i]),str(decimal_outputs[i])]))
        f.write("\n")

def random_test(f, num_reqs):
    #A function that generates random values - writes and then reads
    num_reqs = num_reqs * 2
    f.write(f"{num_reqs}\n")  
    response_req = [1] * (num_reqs // 2) + [0] * (num_reqs // 2)
    hex_addresses = [f"0x{(0x100000000 + 0x1000 * i):X}" for i in range(1,9)] * (num_reqs*9//2)
    decimal_outputs = [random.randint(1,100) for i in range(num_reqs//2)]  
    for i in range (num_reqs // 2):
        f.write(", ".join(['1',str(hex_addresses[i]),str(decimal_outputs[i])]))
        f.write("\n")
    for i in range (num_reqs // 2):
        f.write(", ".join(['0',str(hex_addresses[i]),str(decimal_outputs[i])]))
        f.write("\n")

def create_folder(folder_path):
    if not os.path.exists(os.getcwd() + folder_path):
        print("made")
        os.makedirs(os.getcwd() + folder_path)
    else:
        print("pass")
        pass
main()
