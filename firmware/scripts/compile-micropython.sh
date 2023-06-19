# remember to set the PORT env var to point to your serial port

#make clean BOARD=GENERIC_SPIRAM

make -j 4 DEBUG=1 BOARD=GENERIC_SPIRAM USER_C_MODULES=../../../../gc9a01_mpy/src/micropython.cmake

make BOARD=GENERIC_SPIRAM USER_C_MODULES=../../../../gc9a01_mpy/src/micropython.cmake erase

make BOARD=GENERIC_SPIRAM USER_C_MODULES=../../../../gc9a01_mpy/src/micropython.cmake deploy

