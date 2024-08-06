# root setup
source /home/knutimingdaq01/root/bin/thisroot.sh
# vivado setup
source /tools/Xilinx/Vivado/2024.1/settings64.sh
# programme fpga
cd ./etl_test_fw-v3.2.0
source program.sh
# tamalero setup
cd ../module_test_sw
source setup.sh