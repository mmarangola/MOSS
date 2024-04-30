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
coreFreq = 80000000


pwmFreq = 10000 # output frequency (also the number of pulses per second)
print("Desired output frequency: %f Hz" % (pwmFreq))
dutyCycle = 25 # % duty cycle
print("Desired output duty cycle: %f %%" % (dutyCycle))
clockDivisor = 1 # DIO_EF_CLOCK#_DIVISOR

clockFreq = coreFreq / clockDivisor # DIO_EF_CLOCK frequency
# Note: the roll value and config A are integer values. Both represent a number
# of clock ticks, and you cannot have a fractional number of clock ticks. If
# your PWM frequency and duty cycle do not divide into an integer value for
# these settings, your desired settings are not possible and the values will be
# interpreted as the nearest integer value on the device.
rollValue = float(clockFreq // pwmFreq) # DIO_EF_CLOCK#_ROLL_VALUE
print("Actual output frequency: %f Hz" % (clockFreq/rollValue))
configA = float(dutyCycle * rollValue // 100) # DIO#_EF_CONFIG_A
print("Actual output duty cycle: %f %%" % (configA*100/rollValue))


aNames = [
    "DIO_EF_CLOCK0_ENABLE",
    "DIO_EF_CLOCK0_DIVISOR",
    "DIO_EF_CLOCK0_ROLL_VALUE",
    "DIO_EF_CLOCK0_ENABLE", 
    "DIO%i_EF_ENABLE" % pwmDIO,
    "DIO%i_EF_INDEX" % pwmDIO, 
    "DIO%i_EF_CONFIG_A" % pwmDIO,
    "DIO%i_EF_ENABLE" % pwmDIO, 
    "DIO%i_EF_ENABLE" % counterDIO,
    "DIO%i_EF_INDEX" % counterDIO, 
    "DIO%i_EF_ENABLE" % counterDIO
]
aValues = [
    0, # Disable the DIO_EF clock
    clockDivisor, 
    rollValue, # Set DIO_EF clock divisor and roll for PWM
    1, 
    0, # Enable the clock and disable any features on the PWM DIO
    0, 
    configA, # Set the PWM feature index and duty cycle (configA)
    1, 
    0, # Enable the PWM and disable any features on the counter DIO
    7, 
    1
] # Set the counter feature index and enable the counter.
numFrames = len(aNames)
results = ljm.eWriteNames(handle, numFrames, aNames, aValues)

# Wait 1 second.
time.sleep(2.0)

# Read from the counter. Since we waited 1 second, we expect the value read to
# be close to the PWM frequency (10000 pulses per second)
value = ljm.eReadName(handle, "DIO%i_EF_READ_A" %counterDIO)

print("\nCounter = %f" % (value))

# Disable the DIO_EF clock, PWM output, and counter.
aNames = ["DIO_EF_CLOCK0_ENABLE", "DIO%i_EF_ENABLE" % pwmDIO,
          "DIO%i_EF_ENABLE" % counterDIO]
aValues = [0, 0, 0]
numFrames = len(aNames)
results = ljm.eWriteNames(handle, numFrames, aNames, aValues)

# Close handle
ljm.close(handle)
