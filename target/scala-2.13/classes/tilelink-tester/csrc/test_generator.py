import random
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('file_name', help="File Name")
parser.add_argument('num_tests', type=int, help="Number of Tests")
parser.add_argument('--type', type=str, help="Your age", default='random')

args = parser.parse_args()

def main():  
    filename = args.file_name
    number = args.num_tests
    testtype = args.type

    filename = "test_files/%s_%d_%s" % (args.type, args.num_tests, filename)

    if testtype =='random':
        random_test(filename, number)
    elif testtype == 'single address':
        single_addr_test(filename, number)

def single_addr_test(filename,num_tests):
    address= (0x100000000 + (0x0100 * random.randint(0,10)))
    num_tests = num_tests * 2
    with open(filename, 'w') as f:
        f.write(f"{num_tests}\n")  
        response_req = [1] * (num_tests // 2) + [0] * (num_tests // 2)
        hex_addresses = [f"0x{address:X}" for i in range(num_tests//2)]
        decimal_outputs = [random.randint(1,100) for i in range(num_tests//2)]  
        for i in range (num_tests // 2):
            f.write(", ".join(['1',str(hex_addresses[i]),str(decimal_outputs[i])]))
            f.write("\n")
        for i in range (num_tests // 2):
            f.write(", ".join(['0',str(hex_addresses[i]),str(decimal_outputs[i])]))
            f.write("\n")

def random_test(filename, num_tests):
    #A function that generates random values - writes and then reads
    num_tests = num_tests * 2
    with open(filename, 'w') as f:
        f.write(f"{num_tests}\n")  
        response_req = [1] * (num_tests // 2) + [0] * (num_tests // 2)
        hex_addresses = [f"0x{(0x100000000 + i * 0x0100):X}" for i in range(num_tests//2)]
        decimal_outputs = [random.randint(1,100) for i in range(num_tests//2)]  
        for i in range (num_tests // 2):
            f.write(", ".join(['1',str(hex_addresses[i]),str(decimal_outputs[i])]))
            f.write("\n")
        for i in range (num_tests // 2):
            f.write(", ".join(['0',str(hex_addresses[i]),str(decimal_outputs[i])]))
            f.write("\n")
main()
