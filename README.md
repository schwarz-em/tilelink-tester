# tilelink-tester

## Commands to run chipyard sims (run in sims/vcs):

_TO RUN IN DEBUG MODE:_
make run-binary MODEL=TesterDebugHarness MODEL\_PACKAGE=tlt TOP=TileLinkTester CONFIG=DebugTLTConfig0 CONFIG\_PACKAGE=tlt BINARY=$RISCV/riscv64-unknown-elf/share/riscv-tests/isa/rv64ui-p-simple EXTRA\_SIM\_FLAGS='+tltestfile=/path/to/generators/tilelink-tester/src/main/resources/tilelink-tester/csrc/dataset.txt'

_TO RUN ON THE LPDDR-GENERATOR:_
make MODEL=TLTestHarness MODEL_PACKAGE=ddr CONFIG=DDRTLTConfig CONFIG_PACKAGE=ddr BINARY=$RISCV/riscv64-unknown-elf/share/riscv-tests/isa/rv64ui-p-simple run-binary TOP=TLDDRTester CLOCK_PERIOD=5.0 EXTRA_SIM_FLAGS='+tltestfile=[PATH TO DATASET FILE]'

***^ replace the path to the dataset.txt file with the path on your machine***

## All dataset files ought to be configured as follows:

Line 1: The number of requests being made

Each request must be formatted as follows:
[1 if write, 0 if read operation], 0x[address in hex], [write value if write operation, expected value if read]

**EXAMPLE: (this is a test file with 4 operations)**
4<br>
1, 0x100000100, 59<br>
1, 0x100000100, 82<br>
0, 0x100000100, 59<br>
0, 0x100000100, 82<br>

## How to generate and run tests

Right now, the python generator supports four kinds of tests: (you can easily write your own!)
- "interleaved_test": interleaved reads/writes
- "single_addr_test": a single address, read/written over and over again
- "preload_random_test": random values generated at a specified stride, and then random addresses are selected and read 
- "strided_random_test": random values generated at a specified stride, and then read in the same order they were written

<u>__IMPORTANT__</u>
IN test_executer.py, PLEASE TAKE NOTE OF LINES 19-24 - they are specific to your machine / file_directories an MUST be edited. Apologies for any inconvenience...

<u>python test_generator.py</u>
- 'file_name'; REQUIRED!!! Just whatever name you want to give your tests
- '-num_reqs'; Number of requests per test
- '-type'; Type of tests (see explanation above)
- '-num_tests'; Number of tests
- '-stride'; Stride btwn addresses

(test_generator will default to 1 random test with 10 resuests and an address stride of 256)

<u>python test_executer.py</u>
- 'file_name'; REQUIRED!!! the ABSOLUTE path to the directory where your tests are located. 
- '-v'; will check that your tests located in the specified directory make sense (IE: that your tests are not checking for incorrect values)
- 'dir_name'; the name of the directory you want to label this test run as in your VCS directory (if not specified, will default to timestamp of the run)
- '-c'; will convert the output of your tests to a csv - for performance testing - not robust at all lmfao will be deprioritized atm.
- '-r'; regression testing! will automatically re-generate and run the regression tests for you. Sorry it's not set up yet to let you specify a specific regression test instance / seed, but it's a work in progress.

test_executer will generate the following files within your chipyard/sims/vcs/[dir_name] directory
- Output : a single text file with all Chisel outputs
- diagnostics.csv : a CSV file generated from the regression tests that includes the test name, pass/nopass, and where the test errored
- "some_test_name" : a text file for each test with the associated output from the DRAM model

