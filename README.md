# tilelink-tester

Command to run chipyard sim (run in sims/vcs):

make run-binary MODEL=TesterDebugHarness MODEL\_PACKAGE=tlt TOP=TileLinkTester CONFIG=DebugTLTConfig0 CONFIG\_PACKAGE=tlt BINARY=$RISCV/riscv64-unknown-elf/share/riscv-tests/isa/rv64ui-p-simple EXTRA\_SIM\_FLAGS='+tltestfile=/path/to/generators/tilelink-tester/src/main/resources/tilelink-tester/csrc/dataset.txt'

^ replace the path to the dataset.txt file with the path on your machine

