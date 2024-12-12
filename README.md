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

## How to generate tests

Right now, the python generator supports two kinds of tests - repeatedly writing to a random address,
or random tests that increase in succession

__Here's how to use the CLI:__<br>
python test_generator.py [name of file] [number of tests] {OPTIONAL: --type ['single_address' or 'random']}

if you don't specify a type, it will default to random


__DEFAULT LPDDR PARAMETERS:__<br>
DEBUG = false, IDBITS = 10, ROWBITS = 18,  COLBITS = 8, 
TIMEBITS = 6, RWTIMERBITS = 10, TFAWBITS = 30, BANKBITSTART = 5,
RANKS = 1, BANKS = 8, BURSTLENGTH = 16, DQWIDTH = 16,
BANKDEPTH = 6, QUEUEDEPTH = 256, WRQDEPTH = 256, RDQDEPTH = 256, 
DFIAWIDTH = 6, DFIPHASES = 4, DFIDQMULTIPLE = 4, PHYDQLANESYNC = 3,
PHYOUTPUTRATE = 2, PHYRCVRATE = 2, TLDATAWIDTH = 256