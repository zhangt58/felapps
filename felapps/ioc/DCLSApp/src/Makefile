TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build the IOC application

PROD_IOC = DCLS
# DCLS.dbd will be created and installed
DBD += DCLS.dbd

# DCLS.dbd will be made up from these files:
DCLS_DBD += base.dbd

# Include dbd files from all support applications:
#DCLS_DBD += xxx.dbd

# Add all the support libraries needed by this IOC
#DCLS_LIBS += xxx

# DCLS_registerRecordDeviceDriver.cpp derives from DCLS.dbd
DCLS_SRCS += DCLS_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
DCLS_SRCS_DEFAULT += DCLSMain.cpp
DCLS_SRCS_vxWorks += -nil-

# Add support from base/src/vxWorks if needed
#DCLS_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

# Finally link to the EPICS Base libraries
DCLS_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

