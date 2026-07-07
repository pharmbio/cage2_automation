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
    SC1["Squid Control 1"]
    SC2["Squid Control 2"]
    SC3["Squid Control 3"]
    SC4["Squid Control 4"]
    SQ1["Squid 1"]
    SQ2["Squid 2"]
    SQ3["Squid 3"]
    SQ4["Squid 4"]
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

## Echo Automation

The Echo is driven through a chain of software components spread across three
hosts. The 32-bit micro-service bridges the modern SiLA stack to the legacy
Echo software.

```mermaid
graph TD
    subgraph CTRLH["Control Computer"]
        SILA["SiLA Server"]
    end

    subgraph ECHOH["Echo Computer"]
        MS["32-bit Micro-service"]
        ECHOSW["Echo-Software"]
    end

    subgraph ECHOD["Echo"]
        ESRV["Echo-Server"]
    end

    SILA <-->|socket| MS
    MS <-->|ActiveX| ECHOSW
    ECHOSW <-->|http| ESRV

    classDef computer fill:#8fb8e0,stroke:#3f6fa0,color:#000
    classDef device fill:#9ed48a,stroke:#4f9040,color:#000

    class SILA,MS,ECHOSW computer
    class ESRV device
```

## Power Supply

The platform is powered through five separate power supplies. Each supply feeds a
distinct group of devices:

| Power Supply 1   | Power Supply 2 | Power Supply 3 | Power Supply 4 | Power Supply 5 |
| ---------------- | -------------- | -------------- | -------------- | -------------- |
| Control Computer | Squid Hub      | 405 TS         | Sealer         | Echo           |
| Switch           | Squid Controls | BlueWasher     | Cytomats       | Echo-Computer  |
| Screen           | Squids         | MultiFlowFX    | Fridge         |                |
| Robot            |                |                |                |                |
