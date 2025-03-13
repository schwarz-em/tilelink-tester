import random
import argparse
from pathlib import Path
import subprocess
import os
import sys
import datetime

#EDIT THIS IF YOU WANT TO EDIT YOUR MAKE COMMAND
make_command = r'''make MODEL=TLTestHarness MODEL_PACKAGE=ddr CONFIG=DDRTLTConfig CONFIG_PACKAGE=ddr BINARY=$RISCV/riscv64-unknown-elf/share/riscv-tests/isa/rv64ui-p-simple run-binary TOP=TLDDRTester CLOCK_PERIOD=5.0 EXTRA_SIM_FLAGS='+tltestfile=[FILEPATH]' > [COUNTER]'''

current_directory = os.getcwd()
cwd_index= current_directory.index("tools/tilelink-tester")
sims_directory = current_directory[:cwd_index] + "sims/vcs"
out_directory = current_directory[:cwd_index] + "sims/vcs/output/ddr.TLTestHarness.DDRTLTConfig/rv64ui-p-simple.out"

parser = argparse.ArgumentParser()
parser.add_argument('file_name', help="File Name")
parser.add_argument('-num_reqs', type=int, help="Number of requests per test", default = 0)
parser.add_argument('-type', type=str, help="Type of Test", default='strided_random')
parser.add_argument('-num_tests', type = int, help = "number of tests", default = 1)
parser.add_argument('--run', action='store_true' , help = "run or just generate tests" )
parser.add_argument('-stride', type = int, help = "stride distance", default = 256)
parser.add_argument('-seed', type = int, help = "random seed value", default = 0)
parser.add_argument('-b', '--big', action = 'store_true',  help = "large numbers or small numbers?")

"""
TODO: 
2. Write the Out Files So that the Out Files are Writing Useful Information
3. Blah Blah Blah
"""
"""
example: python test_generator.py random_10_test1 10 random
"""

def generate(folder_path, num_tests, file_name, test_type, num_reqs, stride):
    create_folder(folder_path)
    for i in range (0, num_tests):
        filename = (folder_path + "/%s_%s_%s_%s_%s" % (file_name, i,test_type,num_reqs,stride))
        f = open(filename,'w')
            
        if test_type == 'single_address':
            single_addr_test(f, num_reqs)
        elif test_type == 'strided_random':
            strided_random_test(f, num_reqs, stride)
        elif test_type == 'interleaved':
            interleaved_test(f, num_reqs, stride)
        elif test_type == 'preload_random':
            preload_random_test(f,num_reqs,stride)
        f.close()

            
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
    log_file_directory = sims_directory + "/" + datetime_str
    create_folder(sims_directory + "/" + datetime_str)

    for f in files:
        print(f)
        counter = counter + 1
        final_command = (make_command.replace("[FILEPATH]", str(f))).replace("[COUNTER]", datetime_str +"/test_" + str(counter))
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
    decimal_outputs = [random_val() for i in range(num_reqs //2)]  
    for i in range (num_reqs //2):
        f.write(", ".join(['1',str(hex_addresses[i]),str(decimal_outputs[i])]) + "\n")
        f.write(", ".join(['0',str(hex_addresses[i]),str(decimal_outputs[i])]))
        f.write("\n")

def strided_random_test(f, num_reqs,stride):
    #generates random values - writes and then reads
    num_reqs = num_reqs * 2
    f.write(f"{num_reqs}\n")  
    response_req = [1] * (num_reqs // 2) + [0] * (num_reqs // 2)
    hex_addresses = [f"0x{(0x100000000 + stride * i):X}" for i in range(0,num_reqs)] * (num_reqs*9//2)
    decimal_outputs = [random_val() for i in range(num_reqs//2)]  
    for i in range (num_reqs // 2):
        f.write(", ".join(['1',str(hex_addresses[i]),str(decimal_outputs[i])]))
        f.write("\n")
    for i in range (num_reqs // 2):
        f.write(", ".join(['0',str(hex_addresses[i]),str(decimal_outputs[i])]))
        f.write("\n")
    
def preload_random_test(f,num_reqs,stride):
    write_requests = [(f"0x{(0x100000000 + stride *i):X}", random_val()) for i in range(num_reqs)]
    read_number = random.randint(0,num_reqs)
    read_requests = {}
    f.write(f"{num_reqs + read_number}\n")  
    for i in range(len(write_requests)):
        read_requests[write_requests[i][0]] = write_requests[i][1]
        f.write(", ".join(['1',str(write_requests[i][0]),str(write_requests[i][1])]))
        f.write("\n")
    for j in range(read_number):
        random_key = random.choice(list(read_requests.keys()))
        f.write(", ".join(['0',str(random_key),str(read_requests.get(random_key))]))
        f.write("\n")

def interleaved_test(f, num_reqs,stride):
    f.write(f"{num_reqs}\n")  
    #random list of addresses, data pairs
    write_requests = [(f"0x{(0x100000000 + stride * random.randint(0,num_reqs)):X}", random_val()) for i in range(num_reqs)]
    read_requests = {}
    #for loop, random request
    for i in range(int(num_reqs/2)):
        if ((not random.randint(0,1))and len(read_requests)>0):
            for k in range (2):
                random_key = random.choice(list(read_requests.keys()))
                f.write(", ".join(['0',str(random_key),str(read_requests.get(random_key))]))
                f.write("\n")
        else:
            for k in range (2):
                index_write = random.randint(0,len(write_requests) - 1)
                f.write(", ".join(['1',str(write_requests[index_write][0]),str(write_requests[index_write][1])]))
                f.write("\n")
                read_requests[write_requests[index_write][0]] = write_requests[index_write][1]
                write_requests.pop(index_write)

def create_folder(folder_path):
    print("creating folder at")
    print(folder_path)
    try:
        os.makedirs(folder_path)
    except:
        pass

def set_seed(num):
        # Set a specific seed value
    random.seed(num)
    return 

def random_val():
    ret = 100
    if (big):
        ret = 2**32
    return random.randint(0,ret)

def set_big(val):
    global big
    if (val):
        big = True
    else:
        big = False
    return 

if __name__ == "__main__":
    args = parser.parse_args()

    print("Running Main Function")
    # If --option is not selected, we force the user to provide arg1 and arg2
    if not args.num_reqs or not args.num_tests or not args.type:
        print("Error: You are generating test files. Test name, Type and # of requests must be specified.")
        sys.exit(1)  
    else:
        print("Generating Test Files...")

    req_number = args.num_reqs
    test_type = args.type
    test_name = args.file_name
    test_number = args.num_tests
    stride = args.stride
    seed_num = args.seed
    big_temp = args.big

    set_seed(seed_num)
    set_big(big_temp)
    
    folder_path = ("test_files/%s_%d_%s" % (test_type, test_number, test_name))
    generate(folder_path, test_number, test_name, test_type,req_number, stride)

