#!/usr/bin/env python
import argparse

parser = argparse.ArgumentParser(
    prog="Pulse Generator",
    description="Send laser pulse(s)",
    epilog="Created by Meghan Marangola.  Enjoy the pulses",
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
args = parser.parse_args()

if args.number_pulses == 1 and args.duty_cycle == 100:
    print(f"Single pulse, run leaveOn routine for {args.frequency} seconds")
elif args.number_pulses == 0:
    print(f"Run pwm routine at {args.duty_cycle}% duty cycle and {args.frequency} Hz")
else:
    print(
        f"Create {args.number_pulses} pulse(s) that will be on for "
        f"{args.duty_cycle}% of the time at a "
        f"frequency of {args.frequency} pulses per second"
    )
if args.graph:
    print("Graphing is enabled")
else:
    print("Graphing is disabled")