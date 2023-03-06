  make -j 4 \
    DEBUG=1 \
    BOARD=GENERIC_SPIRAM \
    PORT=/dev/cu.usbserial-14220 \
    USER_C_MODULES=../../../../gc9a01_mpy/src/micropython.cmake all

 make \
    BOARD=GENERIC_SPIRAM \
    PORT=/dev/cu.usbserial-14220 \
    USER_C_MODULES=../../../../gc9a01_mpy/src/micropython.cmake erase

 make \
    BOARD=GENERIC_SPIRAM \
    PORT=/dev/cu.usbserial-14220 \
    USER_C_MODULES=../../../../gc9a01_mpy/src/micropython.cmake deploy