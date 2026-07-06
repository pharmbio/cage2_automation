# Connection Setup

This document describes how the computers and devices of the Cage2 platform are
physically connected via the network switch.

## Network Overview

```mermaid
graph TD
    SW["Network Switch"]

    PF["PF (Robot Arm)<br/>10.10.0.98"]
    CTRL["Control Computer<br/>10.10.0.100<br/><i>SiLA Servers</i><br/><i>Automation</i>"]
    ECHO["Echo Computer<br/>10.10.0.222<br/><i>Micro-service</i><br/><i>Echo-Software</i>"]
    SQUID["Squid Hub<br/>10.10.0.69<br/><i>Squid Coordination</i>"]

    SW --- PF
    SW --- CTRL
    SW --- ECHO
    SW --- SQUID

    ECHODEV["Echo<br/>192.168.0.25"]
    SC1["squid_control 1"]
    SC2["squid_control 2"]
    SC3["squid_control 3"]
    SC4["squid_control 4"]
    SQ1["squid 1"]
    SQ2["squid 2"]
    SQ3["squid 3"]
    SQ4["squid 4"]
    OTHER["Other Devices"]
    NET["Internet / Internal Network"]

    CTRL --- NET
    ECHO --- ECHODEV
    SQUID --- SC1
    SQUID --- SC2
    SQUID --- SC3
    SQUID --- SC4
    SC1 --- SQ1
    SC2 --- SQ2
    SC3 --- SQ3
    SC4 --- SQ4
    CTRL --- |USB| OTHER

    classDef computer fill:#8fb8e0,stroke:#3f6fa0,color:#000
    classDef device fill:#9ed48a,stroke:#4f9040,color:#000
    classDef network fill:#e8c877,stroke:#b3872f,color:#000

    class CTRL,ECHO,SC1,SC2,SC3,SC4,SQUID computer
    class PF,ECHODEV,SQ1,SQ2,SQ3,SQ4,OTHER device
    class SW,NET network
```

Subnet: `10.10.0.0/24`