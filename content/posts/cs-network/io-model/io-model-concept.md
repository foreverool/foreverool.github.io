---
title: 'I/O模型前置概念'
date: '2026-02-08T00:32:32+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- I/O
- Network

menu:
  sidebar:
    name: I/O模型前置概念
    identifier: io-model-concept
    parent: io-model
    weight: 10
---


# I/O模型

Unix 可用的I/O模型主要分为五类：

- 阻塞式I/O
- 非阻塞式I/O
- I/O复用（select / poll）
- 信号驱动I/O
- 异步I/O

一条数据一般会经历两个阶段：

- 等待数据
- 从内核向进程复制数据。

从一个套接字上的输入，一般是等待网络上的数据到达网卡，然后内核从网卡中获取数据并保存在某个缓冲当中，然后将该缓冲的内容复制相应的进程当中。此时进程才可以读取到网络上的数据。

## 第一阶段网卡将数据保存在内核

- 网卡芯片将模拟信号转为数字信号
- DMA传输：网卡通过DMA（Direct Memory Access）技术，直接将数据写入到内核的Ring Buffer当中。
- 网卡向CPU发起一个硬中断，然后告诉CPU数据到了，来处理。

{{< mermaid align="center">}}
sequenceDiagram
        autonumber
        participant nic as 网卡
        participant cpu as CPU 
        participant kenel as 内核
     

        nic ->> nic: 将模拟信号转为数字信号
        note left of nic :第一阶段转换数据

        nic ->> kenel:DMA传输
        note over cpu : 网卡通过DMA技术直接将数据存储到内核缓冲当中即Ring Buffer中


        nic ->> cpu:硬中断
        note right of nic:网卡向CPU发起硬中断，告诉CPU数据来了
{{< /mermaid >}}

## 第二阶段内核协议栈处理

CPU收到硬中断之后，会暂停当前任务，执行终端处理程序：

- 发起软中断：为了不占用CPU太久，硬中断处理程序只做简单标记，然后发起一个软中断，让内核线程稍后处理更为复杂的数据包解析。
- 协议栈解析：内核读取数据，剥离头部信息。
- 放入socket接收缓冲区： 如果数据有效，内核会把有效数据放入该socket对应的内核缓冲区。

此时数据依然在内核当中。

{{< mermaid align="center" >}}
sequenceDiagram
		autonumber
		participant app as 用户进程
		participant cpu as CPU
		participant kenel as 内核
		
		app ->>+ kenel: 系统调用read
		note right of app : 此时进程从用户态转变为内核态
		
	
	
		kenel -->>- app:将内核数据复制到用户进程缓冲区中
		note over cpu: 此时用户进程还是处于内核态
		
		note over app: 此时数据已全部拿到了用户进程中，并且从内核态->用户态
{{< /mermaid>}}

## 第三阶段内核到用户空间

- 系统调用： 进程调用系统调用(read, recv等)，陷入内核态。
- CPU拷贝【比较耗时的步骤】：CPU必须亲自介入，将数据从内核的socket接收缓冲区，完整的复制到用户进程缓冲区。
- 进程唤醒：拷贝完成后，系统调用返回，进程从内核态返回到用户态，终于取走了数据。

{{< mermaid align="center">}}
sequenceDiagram
		autonumber
		participant app as 用户进程
		participant cpu as CPU
		participant kenel as 内核
		
		app ->>+ kenel: 系统调用read
		note right of app : 此时进程从用户态转变为内核态
		
	
	
		kenel -->>- app:将内核数据复制到用户进程缓冲区中
		note over cpu: 此时用户进程还是处于内核态
		
		note over app: 此时数据已全部拿到了用户进程中，并且从内核态->用户态

{{< /mermaid >}}


