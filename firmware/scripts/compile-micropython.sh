# remember to set the PORT env var to point to your serial port
# also, you want to be running this from ~/src/micropython/ports/esp32

#make clean BOARD=GENERIC_SPIRAM

make -j 4 DEBUG=1 BOARD=GENERIC_SPIRAM USER_C_MODULES=../../../../gc9a01_mpy/src/micropython.cmake

# you only have to erase if you want to replace the python code
make BOARD=GENERIC_SPIRAM USER_C_MODULES=../../../../gc9a01_mpy/src/micropython.cmake erase

make BOARD=GENERIC_SPIRAM USER_C_MODULES=../../../../gc9a01_mpy/src/micropython.cmake deploy

