import subprocess
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('file_name', help="File Name")
args = parser.parse_args()

def run_terminal_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Decode and return the output and error (if any)
        output = result.stdout.decode('utf-8')
        error = result.stderr.decode('utf-8')

        return output, error

    except subprocess.CalledProcessError as e:
        # Handle error if the command fails
        return f"Error: {e}", e.stderr.decode('utf-8')

    
def main():  
    filename = "test_files/%s" % (args.file_name)
    fileout = file.open("test_out/%s" % (args.file_name),'w')

    

    with open(filename, 'r') as file:
    for line in file:
        command = line.strip()
        print(command)

        if command.lower() == 'exit':
            print("Exiting the program.")
            break
        
        output, error = run_terminal_command(command)
        file.write(output)
        file.write(error)
        file.write('\n')

        if output:
            print("Output:\n", output)
        if error:
            print("Error:\n", error)

if __name__ == "__main__":
    main()
