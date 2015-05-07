#!../../bin/linux-x86_64/DCLS

## You may have to change DCLS to something else
## everywhere it appears in this file

< envPaths

cd ${TOP}

## Register all support components
dbLoadDatabase "dbd/DCLS.dbd"
DCLS_registerRecordDeviceDriver pdbbase

## Load record instances
#dbLoadRecords("db/xxx.db","user=tongHost")
dbLoadRecords("db/un-ps-emu.db")
dbLoadRecords("db/virtual_fel.db", "PREFIX=UN-BI")
dbLoadRecords("db/laser.db", "LASERID=OPA")
dbLoadRecords("db/ebeam.db", "MACHINE=DCLS")
dbLoadRecords("db/mods.db", "MACHINE=DCLS")

cd ${TOP}/iocBoot/${IOC}
iocInit

## Start any sequence programs
#seq sncxxx,"user=tongHost"
