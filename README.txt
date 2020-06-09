Run:
  Execute 'Main.py'.

  User will be prompted to specify the desired time of day
  at which the program will stop.

  The time range can be altered by changing the time in the users operating system.

Manifest:
  'Main.py'
  'Meter.py'
  'PV_simulator.py'
    ('Output.txt' will be created by 'PV_simulator.py' if one is not already created.
      If 'Output.txt' exists, then it will append new data to the file.)

Environment:
  This program was developed in Ubuntu 18.04 inside of a VMware Workstation Player.

Functionality:
  This program was written in Python 3.8 and uses RabbitMQ 3.8.2 (Erlang 22.2.4) as a broker.

Personal Interpretation of Challenge Requirements:
  The challenge was to replicate listening to a house meter and taking real PV values during a typical day as presented in the PV power curve.
  I felt that the best way to achieve this was to have a constant stream of values coming from the meter in which the 'PV_simulator.py' could sample every few seconds.
  Also the PV values should come from real time. To simulate real PV values for the time of day chosen by the user to listen to the meter.
