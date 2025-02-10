from collections import namedtuple

StartSigns = namedtuple("StartSigns", ["INCOMING", "OUTGOING"])
STARTSIGNS = StartSigns(INCOMING=0xFA, OUTGOING=0xFB)
CMD_GETVERSION = 0x01
CMD_GETVERSIONSTR = 0x02
CMD_GETPARAMETER = 0x03
CMD_SETPARAMETER = 0x04
CMD_GETDATA = 0x05
CMD_GETDATAFIELDS = 0x06
CMD_SETPITCH = 0x0A
CMD_SETROLL = 0x0B
CMD_SETYAW = 0x0C
CMD_SETPANMODE = 0x0D
CMD_SETSTANDBY = 0x0E
CMD_DOCAMERA = 0x0F
CMD_SETSCRIPTCONTROL = 0x10
CMD_SETANGLE = 0x11
CMD_SETPITCHROLLYAW = 0x12
CMD_SETPWMOUT = 0x13
CMD_RESTOREPARAMETER = 0x14
CMD_RESTOREALLPARAMETER = 0x15
CMD_ACTIVEPANMODESETTING = 0x64
CMD_ACK = 0x96
