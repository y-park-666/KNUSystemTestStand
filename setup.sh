# Oscilloscope setup

# root setup
source /home/knutimingdaq01/root/bin/thisroot.sh
# vivado setup
source /tools/Xilinx/Vivado/2024.1/settings64.sh
# programme fpga
#cd ./etl_test_fw-v3.2.0
cd ./etl_test_fw-v3.2.3
#cd ./etl_test_fw-v2.1.11
source program.sh
# tamalero setup
cd ../module_test_sw
source setup.sh
# controlhub run
/opt/cactus/bin/controlhub_start
PROMPT_COMMAND='echo -en "\033]0; Tamalero \a"'
echo "\n"
echo "Please turn on the readout board, using this command:"
echo "ipython3 test_tamalero.py -- --control_hub --kcu 192.168.0.10 --verbose --configuration modulev0b --power_up"
echo "ipython3 test_tamalero.py -- --kcu 192.168.0.10 --verbose --configuration modulev0b --power_up"
echo "\n"
echo "And check if lpGBT gates are locked:"
echo "ipython3 -i test_ETROC.py -- --test_chip --hard_reset --partial --configuration modulev0b --module 1"