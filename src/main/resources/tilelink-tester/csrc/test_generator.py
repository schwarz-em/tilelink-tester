import random

def main():  
    filename = input("Enter the desired file name: ")
    # Ex with 20 test cases
    generate_serial_test(filename, 20)

def generate_serial_test(filename, num_tests):
    #A function that generates random values - writes and then reads
    num_tests = num_tests * 2
    with open(filename, 'w') as f:
        f.write(f"{num_tests}\n")  
        response_req = [1] * (num_tests // 2) + [0] * (num_tests // 2)
        hex_addresses = [f"0x{(0x100000000 + i * 0x1000):X}" for i in range(num_tests//2)]
        decimal_outputs = [random.randint(1,100) for i in range(num_tests//2)]  
        for i in range (num_tests // 2):
            f.write(", ".join(['1',str(hex_addresses[i]),str(decimal_outputs[i])]))
            f.write("\n")
        for i in range (num_tests // 2):
            f.write(", ".join(['0',str(hex_addresses[i]),str(decimal_outputs[i])]))
            f.write("\n")
main()
