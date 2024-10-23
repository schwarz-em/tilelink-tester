import random

def generate_test_file(filename, num_tests):
    num_tests = num_tests * 2
    with open(filename, 'w') as f:
        f.write(f"{num_tests}\n")  
        response_req = [1] * (num_tests // 2) + [0] * (num_tests // 2)
        hex_addresses = [f"0x{(0x100000000 + i * 0x1000):X}" for i in range(num_tests//2)]
        decimal_outputs = [random.randint(1,100) for i in range(num_tests//2)]  
        for i in range (num_tests//2):
            f.write(", ".join([str(response_req[i]),str(hex_addresses[i]),str(decimal_outputs[i])]))
            f.write("\n")

# Ex with 20 test cases
generate_test_file('test_data.txt', 20)