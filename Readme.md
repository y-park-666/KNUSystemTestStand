경북대학교 ETL 시스템 테스트 스탠드
=============

사전 구매 리스트 및 요구조건
-------------
1. 운영체제: Ubuntu 20.04 or higher, Centos 7 or higher
2. 사전 요구 패키지: ROOT, ipbus, boost, pugixml, ipython3
3. FPGA: AMD Xilinx Ultrascale KCU105
4. 오실로스코프: Lecroy Waverunner 8208hd (권장)

PCB, Sensor, Electronics
-------------
1. PCB: ETL module V0b, Readout Board v2.2 with VTRX+, Power Adapter
2. Sensor: FBK UFSD-K1, UFSD-K2 LGADs
3. Electronics: TSMC ETROC2 Prototype (16x16)

레이저 사양
-------------
1065 nm IR Photon

FPGA 펌웨어 및 테스트 소프트웨어
-------------
etl_test_fw-v3.2.0
Tamalero SW (module_test_sw)

사용 방법
-------------
### 클론 및 환경설정
```
git clone https://github.com/resisov/KNUSystemTestStand
cd KNUSystemTestStand
source setup.sh
```
### 오실로스코프 통신 테스트
```
cd OscilloscopeControl
python oscilloscope_control_v0_3.py
```
### Readout board turn on (On debugging)
```
ipython3 test_tamalero.py -- --kcu 192.168.0.10 --verbose --configuration modulev0b --power_up
```