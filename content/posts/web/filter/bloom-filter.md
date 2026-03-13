---
title: '布隆过滤器'
date: '2026-03-13T17:32:46+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- bloom
- filter
- Redisbloom

menu:
  sidebar:
    name: 布隆过滤器
    identifier: bloom-filter
    parent: filter
    weight: 10
---


# 布隆过滤器

布隆过滤器是一个节省空间的概率型数据结构，其本质是**一个很长的二进制向量和一些列哈希函数**。

我们如果判断一个元素是否存在，要么使用哈希，要么使用集合。但是这两个数据结构都会存储着元素对象本身，并且占用空间是根据元素本身的字节大小。

比如一个`URL`，我们假设其长度都为`100个字符`。那么如果是根据`ascii`存储，一个`URL`所占用字节空间就是100字节，也就是100`Bytes`。那么我们如果需要判断一个`URL`是否在1亿`URL`集合中是否存在。那么理论上需要占用**总字节数：** $100 \times 10^8 = 10,000,000,000 \text{ Bytes}$，也就是$10,000,000,000 \div 1024^3 \approx \mathbf{9.31 \text{ GB}}$。

对于内存空间有限的情况下，比如`2026-3-13`日当前内存条贵的离谱❗我们如何才能更省内存，判断一个URL是否存在呢？ 那么就可以使用布隆过滤器。

## 布隆过滤器的核心原理

{{< mermaid align="center">}}

graph LR
    subgraph Initialization ["布隆过滤器初始化"]
        start("开始") --> A[BitArray位数组-全部为0]
        A --> |哈希函数个数 K| B[哈希函数 H1, H2, H3...]
    end

    subgraph AddElement["添加元素 'Apple'"]
        Apple --> H1_A[H1'Apple']
        Apple --> H2_A[H2'Apple']
        Apple --> H3_A[H3'Apple']

        H1_A --> Array_A1[标记位数组的第X1位为1]
        H2_A --> Array_A2[标记位数组的第X2位为1]
        H3_A --> Array_A3[标记位数组的第X3位为1]
    end

    subgraph AddElement2["添加元素 'Banana'"]
        Banana --> H1_B[H1'Banana']
        Banana --> H2_B[H2'Banana']
        Banana --> H3_B[H3'Banana']

        H1_B --> Array_B1[标记位数组的第Y1位为1]
        H2_B --> Array_B2[标记位数组的第Y2位为1]
        H3_B --> Array_B3[标记位数组的第Y3位为1]
    end

    subgraph BloomFilterStructure ["布隆过滤器内部状态"]
        Array_A1 & Array_A2 & Array_A3 & Array_B1 & Array_B2 & Array_B3 -- 影响 --> BitArrayUpdated[位数组 部分位已为 1]
    end

    subgraph QueryElement_Exists["查询元素 'Apple'"]
        Q_Apple --> Q_H1_A[H1'Apple']
        Q_Apple --> Q_H2_A[H2'Apple']
        Q_Apple --> Q_H3_A[H3'Apple']

        Q_H1_A -- 检查对应位是否为 1 --> Check1_A
        Q_H2_A -- 检查对应位是否为 1 --> Check2_A
        Q_H3_A -- 检查对应位是否为 1 --> Check3_A

        Check1_A & Check2_A & Check3_A -- 全部为 1 --> Result_Exists[结果: 'Apple' 可能存在]
    end

    subgraph QueryElement_NotExists["确实不存在"]
        Q_Orange --> Q_H1_O[H1'Orange']
        Q_Orange --> Q_H2_O[H2'Orange']
        Q_Orange --> Q_H3_O[H3'Orange']

        Q_H1_O -- 检查对应位是否为 1 --> Check1_O
        Q_H2_O -- 检查对应位是否为 1 --> Check2_O
        Q_H3_O -- 检查对应位是否为 1 --> Check3_O

        Check1_O & Check2_O & Check3_O -- 其中某位为 0 --> Result_NotExists[结果: 肯定不存在]
    end

    subgraph QueryElement_FalsePositive["实际不存在，但误判"]
        Q_Grape --> Q_H1_G[H1'Grape']
        Q_Grape --> Q_H2_G[H2'Grape']
        Q_Grape --> Q_H3_G[H3'Grape']

        Q_H1_G -- 检查对应位是否为 1 --> Check1_G
        Q_H2_G -- 检查对应位是否为 1 --> Check2_G
        Q_H3_G -- 检查对应位是否为 1 --> Check3_G

        Check1_G & Check2_G & Check3_G -- 全部为 1 (巧合) --> Result_FalsePositive[结果 可能存在误判]
        style Result_FalsePositive fill:#f96,stroke:#333
    end

  
{{< /mermaid >}}


布隆过滤器底层基本上就是一个大的二进制数组，然后搭配多个哈希函数。

### 添加元素

如果我们需要为一个URL或者ID等数据，添加到布隆过滤器中。需要执行以下步骤：

- 通过调用多个哈希函数，H1,H2,H3..分别计算出二进制数组，哪个位置需要将1填入。
- 然后将该位置的比特位写入1。

这里需要注意的是，由于多个对于不同元素hash可能产生碰撞，所以有可能某个位置的1是多个元素共享的。这也就导致了布隆过滤器无法删除元素。

### 查询元素

- 分别执行H1,H2,H3…哈希函数，计算出每个位置中比特位，如果有一个哈希函数返回的位置中是0，那么就判断该元素不存在。
- 由于可能产生哈希碰撞，比如5个哈希函数，返回的位置都是1，但是实际上并没有添加该元素到布隆过滤器中，导致返回结果存在的结果。这就是误判。

我们可以知道越多的哈希函数和越大的二进制数组空间，产生误判的概率就越低，但是所消耗的CPU资源就越多空间也会多一点。

## 如何解决布隆过滤器无法删除元素

由于哈希碰撞导致同一位0或者1被多个元素所共享，那么就不能轻易将这个位置1变为0。所以一般布隆过滤器不能删除元素，当然也有支持删除的布隆过滤器比如`Counting Bloom Filter`。

- 所以解决布隆过滤器无法删除元素最简单的方案就是使用计数布隆过滤器。只是会增加一些存储空间。

- 要解决删除一个元素很麻烦，但是重建布隆过滤器就很简单。所以一般可以在业务请求低峰的时候，重建布隆过滤器，将数据库的该类型的元素依次遍历，重新写入布隆过滤器中。

## RedisBloom插件

`RedisBloom`是`Redis`官方推荐使用的插件，专门解决海量数据快速查询是否存在。其不仅实现了基础的布隆过滤吧器，也实现了计数布隆过滤器，布谷鸟过滤器等变体。完美解决了原生布隆过滤器无法删除和误判率高的问题。

`RedisBloom`是一个套件，不是单一的布隆过滤器实现，可以根据不同的业务场景原则不同的过滤器。

| 数据结构                | 核心能力                                   | 适用场景                                   |
| ----------------------- | ------------------------------------------ | ------------------------------------------ |
| 基础布隆过滤器（Bloom） | 快速添加 / 查询，极致省空间，不支持删除    | 缓存穿透、垃圾邮件过滤（无需删除的场景）   |
| 计数布隆过滤器（CBF）   | 支持安全删除单个元素，空间占用略高         | 需要动态增删元素的场景（如购物车、黑名单） |
| 布谷鸟过滤器（Cuckoo）  | 删除效率更高，空间利用率优于 CBF，支持迭代 | 高频删除、需要遍历元素的场景               |
| Top-K 过滤器            | 统计高频元素（类似布隆 + 计数器）          | 热门商品、高频访问 IP 统计                 |



