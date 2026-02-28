---
title: 'Explain 工具'
date: '2026-02-28T11:32:33+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- 索引
- 索引失效
- 索引优化工具
menu:
  sidebar:
    name: Explain 工具
    identifier: explain-tools
    parent: mysql-index
    weight: 10
---


# EXPLAIN用法

`EXPLAIN`是`MySQL`模拟优化器执行SQL查询语句，告诉你`MySQL`是如何处理你的SQL的。

只需在你的 `SELECT`、`DELETE`、`INSERT`、`REPLACE` 或 `UPDATE` 语句前加上 `EXPLAIN` 即可：

```sql
EXPLAIN SELECT * FROM actor WHERE last_name="DAVIS";
EXPLAIN SELECT * FROM actor WHERE last_name="DAVI"+"S";
```

## 核心字段

当你使用`EXPLAIN`后，你会看到一张表，表中的每个字段如下：

- `type`: 链接类型，性能监控的核心，它显示了查询是如何搜索数据的，性能从优到差依次为：
  - system/const：命中主键或者唯一索引，且匹配一行。速度极快。
  - eq_ref： 多表连接时，使用了主键或唯一索引。
  - ref: 使用了非唯一索引（普通索引）进行等值匹配。
  - range: 索引范围扫描（如：ID>10、Between、IN）。
  - index: 全索引扫描（遍历了索引树，但是没有遍历数据文件）
  - ALL: 全表扫描。性能最差
- `key`实际使用的索引
  - 如果为NULL，说明没用到索引。
  - 如果用到了索引，会显示索引名称/
- `key_len`索引使用的字节长度
  能帮你判断联合索引中到底匹配了多少列。长度越长，说明索引匹配越充分。
- `row`预估扫描行数
  MySQL认为执行这个查询需要扫描的行数，数据越小越好。
- `Extra`额外信息，调优风向标
  - Using index： 出现了 覆盖索引，不需要回表，性能优秀。
  - Using where: 过滤条件不在索引里，需要回表查询。
  - Using filesort：危险信号，MySQL需要额外排序操作，通常因为ORDER BY没有用到索引。
  - Using temporary:极度危险。MySQL创建了临时表，通常出现在Order BY没有用到索引时。



## 8.0版本之后`EXPLAIN`

在`MySQL`8.0之后，`EXPAIN`引入了更直观的`TREE`格式。

阅读顺序变为由内而外，由下而上。

### 关键`Operator`解读：

- Rows fetched before execution ：
  表示直接使用了主键索引查询数据，对应之前的type=const/system。

- covering index lookup:
  使用了覆盖索引

- index lookup/ index scan:
  - index lookup: 使用了索引定位对应（type=ref/eq_ref）
  - index scan:扫描了整个索引树（对应type=index）
- table scan： 全表扫描，对应type=ALL，性能最差。
- Filter: 对扫描出的结果进行条件过滤。对应`Extra:Using where`。
- Nested loop inner join: 嵌套循环连接。最基础的多表关联方式。
- Hash join: 
  - 当关联字段没有索引时，8.0会自动使用hash join取代慢的离谱的block nested loop。
  - 极大地提升了无索引关联查询的速度。
- Agreegate:执行聚合操作。如：COUNT,SUM,GROUP BY。

### 指标深度解析：

- Cost ：成本 分数
  - 这是MySQL优化器根据磁盘IO、CPU计算综合得出的逻辑值。
  - 越低越好。优化器会对比多种方案，选择COST最低的那条路线。
- ROWS：预估行数
  - 优化器预估这个操作需要处理的数据行数。
  - 不一定100%正确。


### EXPLAIN ANALYZE

用法：`EXPLAIN ANALYZE`

它会输出：

- actual time:实际花费时间（格式为：first_row..last_row）
- actual rows:实际返回的行数。
- Loops： 该操作循环了多少次。