"""
Enables a 10 kHz PWM output and high-speed counter, waits 1 second, and reads
the counter. If you jumper the counter to the PWM the value read from the
counter should be close to 10000.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    Multiple Value Functions(such as eWriteNames):
        https://labjack.com/support/software/api/ljm/function-reference/multiple-value-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Digital I/O:
        https://labjack.com/support/datasheets/t-series/digital-io
    Extended DIO Features:
        https://labjack.com/support/datasheets/t-series/digital-io/extended-features
    PWM Out:
        https://labjack.com/support/datasheets/t-series/digital-io/extended-features/pwm-out
    High-Speed Counter:
        https://labjack.com/support/datasheets/t-series/digital-io/extended-features/high-speed-counter

Note:
    Our Python interfaces throw exceptions when there are any issues with
    device communications that need addressed. Many of our examples will
    terminate immediately when an exception is thrown. The onus is on the API
    user to address the cause of any exceptions thrown, and add exception
    handling when appropriate. We create our own exception classes that are
    derived from the built-in Python Exception class and can be caught as such.
    For more information, see the implementation in our source code and the
    Python standard documentation.
"""
import time

from labjack import ljm
import numpy as np
import matplotlib.pyplot as plt


def pulse():
    # dutyCycle became pulseLength in __microseconds__ (because of pwmFreq)

    pwmFreq = 10_000 # output frequency (also the number of pulses per second)
    print("Desired output frequency: %f Hz" % (pwmFreq))
    pulseLength = 10 # % duty cycle
    numPulses = 7
    print("Desired output duty cycle: %f %%" % pulseLength)
    clockDivisor = 8 # DIO_EF_CLOCK#_DIVISOR

    clockFreq = coreFreq / clockDivisor # DIO_EF_CLOCK frequency
    # Note: the roll value and config A are integer values. Both represent a number
    # of clock ticks, and you cannot have a fractional number of clock ticks. If
    # your PWM frequency and duty cycle do not divide into an integer value for
    # these settings, your desired settings are not possible and the values will be
    # interpreted as the nearest integer value on the device.
    rollValue = float(clockFreq // pwmFreq) # DIO_EF_CLOCK#_ROLL_VALUE
    print("Actual output frequency: %f Hz" % (clockFreq/rollValue))
    configA = float(pulseLength * rollValue // 100) # DIO#_EF_CONFIG_A
    print("Actual output duty cycle: %f %%" % (configA*100/rollValue))
    print(f"configA: {configA}")

    aNames = [
        "DIO_EF_CLOCK0_ENABLE",  # checked
        "DIO_EF_CLOCK0_DIVISOR",  # checked
        "DIO_EF_CLOCK0_ROLL_VALUE",  # checked
        "DIO_EF_CLOCK0_ENABLE",   # checked
        "DIO%i_EF_ENABLE" % pwmDIO,  # checked
        "DIO%i" %pwmDIO,  # Added
        "DIO%i_EF_INDEX" % pwmDIO, 
        "DIO%i_EF_CONFIG_A" % pwmDIO,
        "DIO%i_EF_CONFIG_B" % pwmDIO,
        "DIO%i_EF_CONFIG_C" % pwmDIO,
        "DIO%i_EF_ENABLE" % pwmDIO, 
    ]

    aValues = [
        0, # Disable the DIO_EF clock
        clockDivisor, 
        rollValue, # Set DIO_EF clock divisor and roll for PWM
        1, 
        0, # Enable the clock and disable any features on the PWM DIO
        0, # Added
        2,  # CHanged from 0 to 2
        configA, # Set the PWM feature index and duty cycle (configA)
        0,  #Added (config B)
        numPulses, #Added (config C)
        1, 
    ] # Set the counter feature index and enable the counter.
    if len(aNames) != len(aValues):
        raise("Check your settings")

    numFrames = len(aNames)
    print("Starting Signal")
    results = ljm.eWriteNames(handle, numFrames, aNames, aValues)

    # variables
    # pwmFreq - maximum potential pulses per second
    # pulseLength = duty cycle - percent of each cycle that the laser is on

    RES = 100
    PULSES_LEN = numPulses/pwmFreq


    index = np.arange(0,pwmFreq*PULSES_LEN*RES)
    y = np.zeros(len(index))

    count = 0

    for i in range(len(index)//100):
        for j in range(100):
            if j<pulseLength:
                y[count] = 5
            else:
                y[count] = 0
            count = count + 1

    plt.plot(index/(pwmFreq*RES),y)
    plt.title("Expected Output")
    plt.ylabel("V Out (Volts)")
    plt.xlabel("time (seconds)")

    plt.show()


    # Wait 1 second.
    time.sleep(1.0)
    print("Stopping Signal")
    # Disable the DIO_EF clock, PWM output, and counter.
    aNames = ["DIO_EF_CLOCK0_ENABLE", "DIO%i_EF_ENABLE" % pwmDIO,
            "DIO%i_EF_ENABLE" % counterDIO]
    aValues = [0, 0, 0]
    numFrames = len(aNames)
    results = ljm.eWriteNames(handle, numFrames, aNames, aValues)

def shutdown():
    # Close handle
    ljm.close(handle)
    print("Exiting")




def leaveOn(t):
    """ Leave the laser diode on for t seconds"""
    # reference for this code: <https://github.com/labjack/labjack-ljm-python/blob/master/Examples/Basic/eWriteAddress.py>
    address = 2000 # DIO0; this is listed here <https://support.labjack.com/docs/3-1-modbus-map-t-series-datasheet> as address for all DIO ports
    dataType = ljm.constants.UINT16
    value = 1  # HIGH logic level

    # alternate code if above does not work
    # dataType = ljm.constants.FLOAT32
    # value = 5.0 # 5 volts
    ljm.eWriteAddress(handle, address, dataType, value)
    
    x_vals = np.arange(t)
    y_vals = np.zeros(len(x_vals))
    y_vals[::] = 5
    plt.plot(x_vals, y_vals)
    plt.title("Expected Output")
    plt.ylabel("V Out (Volts)")
    plt.xlabel("time (seconds)")
    plt.show()

    print(f"{t} seconds of pulse")
    time.sleep(t)

    ljm.eWriteAddress(handle, address, 0, dataType)
    
    print(f"Pulse ended")


# Three possible scenarios:
#
# 1. On for length of time, then off (separate file)
#       Use basic python timer.  Set pin High, wait in python, then set pin low
# 2. Pulse (this code)
# 3. Pulse train with number of pulses at given frequency and duration   
#




 # Open LabJack
handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier


info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

deviceType = info[0]

# Configure the PWM output and counter.
# For the T7, use FIO0 (DIO0) for the PWM output
# Use CIO2 (DIO18) for the high speed counter
pwmDIO = 0
counterDIO = 18
# T7 core frequency is 80 MHz
coreFreq = 80_000_000

pulse()
# leaveOn(10)
shutdown()
