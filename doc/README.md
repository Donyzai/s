# SOST - Stability and System Observation Tool

## Overview
SOST (Stability and System Observation Tool) is a comprehensive testing and monitoring tool designed for system stability analysis across various Linux distributions. It provides features for hardware monitoring, system information collection, error detection, and automated testing workflows.

## Features

### Core Functionality
- System stability testing with configurable test models
- Hardware information collection (CPU, memory, sensors, etc.)
- Error detection and logging across multiple subsystems
- Automated testing workflows for various hardware components
- Multi-distribution support (RHEL, Ubuntu, OpenEuler, Kylin, etc.)

### Key Features by Version

#### v1.0.8 (Development)
- Optimized data collection and comparison processes
- Added BMC test credential recording
- Global command for system reset
- Improved sensor data acquisition
- Enhanced logging management
- Added iBMC CPU/memory information collection
- Improved error handling and reporting

#### v1.0.7
- Improved SEL log handling
- Ubuntu 22.03 compatibility fixes
- Added lsusb information check
- Enhanced iBMC adapter functionality
- Improved self-startup methods
- Refined error comparison logic
- Added online update capability
- Enhanced logging system

#### v1.0.6
- Comprehensive IPMITOOL error checking
- Separated BMC/os/system checks
- Added stress test capability
- Enhanced dmesg error checking for specific projects
- Improved disk information display
- IPMItool adaptation for iBMC
- Optimized timing tests
- Added power cycle test models

#### v1.0.5
- Improved hardware information collection (HDD, PCIE, etc.)
- Added HTML result reporting
- Enhanced restart time failure detection
- Added RHEL graphical testing
- Fixed various installation issues
- Added BMC reset test capabilities
- Improved logging system

#### v1.0.4
- Added IPMITOOL LAN data recording
- Enhanced OSIP control point acquisition
- Added debug command shortcuts
- Improved web console functionality
- Added SWC manager service
- Enhanced logging system
- Added custom test case capability
- Added dual IP/BMC status check

#### v1.0.3
- Added BMC sensor collection
- Enhanced BMC log checking
- Fixed BMC SEL error handling
- Improved logging system
- Added BMC chip detection
- New BMCTool utilities
- Added stability test types
- Enhanced IPMI sensor comparison

#### v1.0.2
- Fixed Kylin system GUI/text conflicts
- Resolved bash profile clearing issues
- Enhanced PSU information collection
- Added AC lost test configuration
- Improved BMC/dmesg detection order
- Added BMC liveness check

## Installation

```bash
# Clone the repository

Tty-Test-CS : wget http://192.168.60.138/sost/sost-v1.0.7-Release.tar && tar -xvf sost-v1.0.7-Release.tar && cd sost-v1.0.7-Release && python3 sost_install.py && cd && sost -h

Tty-Test-SZ : wget http://172.19.1.24/sost/sost-v1.0.7-Release.tar && tar -xvf sost-v1.0.7-Release.tar && cd sost-v1.0.7-Release && python3 sost_install.py && cd && sost -h   
