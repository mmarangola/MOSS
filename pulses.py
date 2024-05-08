#!/usr/bin/env python

"""
Creates one of three things: a) a pulse that on for a specified time interval, b) a series of pulses at 
a given duty cycle and frequency, or c) a modulated pulse for a specified time interval at a given 
frequency. Type pulses.py -h for help.
"""

import time
from labjack import ljm
import numpy as np
import matplotlib.pyplot as plt
import argparse


def pulse(freq=10_000, dutyCycle=50, numPulses=7):
    """ Send in a given number of pulses at a given frequency and duty cycle.

    Args:
        freq (_type_, optional): _description_. Defaults to 10_000.
        dutyCycle (int, optional): _description_. Defaults to 50.
        numPulses (int, optional): _description_. Defaults to 7.
    """
    # dutyCycle became pulseLength in __microseconds__ (because of pwmFreq)

    freq = freq # output frequency (also the number of pulses per second)
    # print("Desired output frequency: %f Hz" % freq)
    dutyCycle = dutyCycle # % duty cycle
    numPulses = numPulses
    # print("Desired output duty cycle: %f %%" % dutyCycle)
    clockDivisor = 8 # DIO_EF_CLOCK#_DIVISOR

    clockFreq = coreFreq / clockDivisor # DIO_EF_CLOCK frequency

    # rollValue and configA represent numbers of clock ticks -> integer division
    rollValue = float(clockFreq // freq) # DIO_EF_CLOCK#_ROLL_VALUE 
    print("Actual output frequency: %f Hz" % (clockFreq/rollValue))
    configA = float(dutyCycle * rollValue // 100) # DIO#_EF_CONFIG_A
    print("Actual output duty cycle: %f %%" % (configA*100/rollValue)) 

    aNames = [
        "DIO_EF_CLOCK0_ENABLE",  # checked
        "DIO_EF_CLOCK0_DIVISOR",  # checked
        "DIO_EF_CLOCK0_ROLL_VALUE",  # checked
        "DIO_EF_CLOCK0_ENABLE",   # checked
        "DIO%i_EF_ENABLE" % pwmDIO,  
        "DIO%i" %pwmDIO, 
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
        raise("Check list lengths")

    numFrames = len(aNames)
    
    # variables
    # pwmFreq - maximum potential pulses per second
    # pulseLength = duty cycle - percent of each cycle that the laser is on
    
    if args.graph:
        RES = 100
        PULSES_LEN = numPulses/freq

        print("Close plot to start signal.")

        index = np.arange(0,freq*PULSES_LEN*RES)
        y = np.zeros(len(index))

        count = 0

        for i in range(len(index)//100):
            for j in range(100):
                if j<dutyCycle:
                    y[count] = 5
                else:
                    y[count] = 0
                count = count + 1

        plt.plot(index/(freq*RES),y)
        plt.title("Expected Output")
        plt.ylabel("V Out (Volts)")
        plt.xlabel("time (seconds)")
        plt.show()


    
    print("Starting Signal")
    results = ljm.eWriteNames(handle, numFrames, aNames, aValues)


    # Wait length seconds.
    time.sleep(PULSES_LEN)
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


def leaveOn(on_seconds:float):
    """ Leave the laser diode on for t seconds.

    Args:
        on_seconds (float): time laser diode is on
    """
    # reference for this code: <https://github.com/labjack/labjack-ljm-python/blob/master/Examples/Basic/eWriteAddress.py>
    address = 2000 # DIO0; this is listed here <https://support.labjack.com/docs/3-1-modbus-map-t-series-datasheet> as address for all DIO ports
    dataType = ljm.constants.UINT16
    value = 1  # HIGH logic level

    # alternate code if above does not work
    # dataType = ljm.constants.FLOAT32
    # value = 5.0 # 5 volts
    
    
    if args.graph:
        x_vals = np.arange(on_seconds)
        y_vals = np.zeros(len(x_vals))
        y_vals[::] = 5

        print("Close plot to start signal.")
        plt.plot(x_vals, y_vals)
        plt.title("Expected Output")
        plt.ylabel("V Out (Volts)")
        plt.xlabel("time (seconds)")
        plt.show()

    ljm.eWriteAddress(handle, address, dataType, value)
    print(f"{on_seconds} seconds of pulse")
    time.sleep(on_seconds)

    ljm.eWriteAddress(handle, address, 0, dataType)
    
    print(f"Pulse ended")


def pwm(freq, dutyCycle, duration):
    pwmFreq = freq # output frequency (also the number of pulses per second)
    print("Desired output frequency: %f Hz" % (pwmFreq))
    # % duty cycle
    print("Desired output duty cycle: %f %%" % (dutyCycle))
    clockDivisor = 1 # DIO_EF_CLOCK#_DIVISOR

    clockFreq = coreFreq / clockDivisor 
    rollValue = float(clockFreq // pwmFreq) # DIO_EF_CLOCK#_ROLL_VALUE
    print("Actual output frequency: %f Hz" % (clockFreq/rollValue))
    configA = float(dutyCycle * rollValue // 100) # DIO#_EF_CONFIG_A
    print("Actual output duty cycle: %f %%" % (configA*100/rollValue))


    aNames = ["DIO_EF_CLOCK0_ENABLE",
            "DIO_EF_CLOCK0_DIVISOR", 
            "DIO_EF_CLOCK0_ROLL_VALUE",
            "DIO_EF_CLOCK0_ENABLE", 
            "DIO%i_EF_ENABLE" % pwmDIO,
            "DIO%i_EF_INDEX" % pwmDIO, 
            "DIO%i_EF_CONFIG_A" % pwmDIO,
            "DIO%i_EF_ENABLE" % pwmDIO, 
            "DIO%i_EF_ENABLE" % counterDIO,
            "DIO%i_EF_INDEX" % counterDIO, 
            "DIO%i_EF_ENABLE" % counterDIO]
    aValues = [0, # Disable the DIO_EF clock
            clockDivisor, # Set DIO_EF clock divisor
            rollValue, #  Set roll for PWM
            1,  # Enable the clock 
            0, #  Disable any features on the PWM DIO
            0, # Set the PWM feature index
            configA, # Set the duty cycle (configA)
            1, # Enable the PWM 
            0, # Disable any features on the counter DIO
            7, # Set the counter feature index
            1] # Enable the counter.
    
    numFrames = len(aNames)

    if args.graph:
        # pwmFreq - maximum potential pulses per second
        # duration - total time the laser is flashing (seconds)
        # dutyCycle - percent of each cycle that the laser is on

        RES = 100
        PULSES_LEN = duration

        index = np.arange(0,freq*PULSES_LEN*RES)
        y = np.zeros(len(index))

        count = 0

        for i in range(len(index)//100):
            for j in range(100):
                if j<dutyCycle:
                    y[count] = 5
                else:
                    y[count] = 0
                count = count + 1

        print("Close plot to start signal.")

        plt.plot(index/(pwmFreq*RES),y)
        plt.title("Expected Output")
        plt.ylabel("V Out (Volts)")
        plt.xlabel("time (seconds)")
        print("line 219")
        plt.show()


    print("Starting pwm")
    results = ljm.eWriteNames(handle, numFrames, aNames, aValues)
    
    # Wait duration seconds.
    time.sleep(duration)

    print("Stopping pwm")
    # Disable the DIO_EF clock, PWM output, and counter.
    aNames = ["DIO_EF_CLOCK0_ENABLE", "DIO%i_EF_ENABLE" % pwmDIO,
            "DIO%i_EF_ENABLE" % counterDIO]
    aValues = [0, 0, 0]
    numFrames = len(aNames)
    results = ljm.eWriteNames(handle, numFrames, aNames, aValues)




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

# command line functionality (imported argparse above)

parser = argparse.ArgumentParser(
    prog="Pulse Generator",
    description="Send laser pulse(s)",
    epilog="Created by Meghan Marangola.",
)
parser.add_argument(
    "-n",
    "--number_pulses",
    type=int,
    help="The duration the pulse is on. If set to 0, pwn function will run",
    required=True,
)
parser.add_argument(
    "-d",
    "--duty_cycle",
    type=float,
    help="Percentage of time the pulse is on. If set to 100, leaveOn function will run.",
    default=50,
)
parser.add_argument(
    "-f",
    "--frequency",
    type=int,
    help="Maximum number of pulses per second",
    default=10_000,
)
parser.add_argument(
    "-g",
    "--graph",
    action="store_true",
    help="Create a graph of the pulses",
)

parser.add_argument(
    "-p",
    "--pwm_duration",
    type=float,
    help="Duration of pwm or leaveOn",
)

args = parser.parse_args()

if args.number_pulses == 1 and args.duty_cycle == 100:
    print(f"Single pulse, run leaveOn routine for {args.frequency} seconds")
    leaveOn(args.frequency)
elif args.number_pulses == 0:
    print(f"Run pwm routine at {args.duty_cycle}% duty cycle and {args.frequency} Hz, for {args.pwm_duration} seconds")
    pwm(args.frequency, args.duty_cycle, args.pwm_duration)
else:
    print(
        f"Create {args.number_pulses} pulse(s) that will be on for "
        f"{args.duty_cycle}% of the time at a "
        f"frequency of {args.frequency} pulses per second"
    )
    pulse(args.frequency, args.duty_cycle, args.number_pulses)
if args.graph:
    print("Graphing is enabled")
else:
    print("Graphing is disabled")

shutdown()
