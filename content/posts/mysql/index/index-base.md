---
title: '索引基本概念'
date: '2026-02-28T02:09:32+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- 索引
- 索引失效
menu:
  sidebar:
    name: 索引基本概念
    identifier: index-base
    parent: mysql-index
    weight: 10
---


# 索引

## 前言

索引在官网中描述的位置是在`Optimization and Index`，可以看出索引被设计出来是为了优化查询的，官网中是这样描述索引的：**Indexes are used to find rows with specific column values quickly.**

所以说使用了索引可以快速的查找具体的记录`record`。

索引是被存储在一种数据结构中，由于在`MySQL`中索引有很多种，不同的存储引擎在实现索引的时候，使用不同的数据结构。大多数索引是被存储在`B-trees`中，但是有一些存储引擎使用的是`hash indexs, b+tree indexs, FULLTEXT indexs`等。

本文主要描述`Innodb`存储引擎中的索引结构，`b+tree`。从名称可以看到这个数据结构是一种`tree`的结构。

## 如何定义一个索引

定义一个索引的时候可以使用`PRIMARY KEY, UNIQUE, INDEX and FULLTEXT`关键字。在创建`table`的过程中，指定某个字段属性为索引。在`Innodb`存储引擎下，如果在创建表的时候没有定义主键，唯一字段的话，`MySQL`会找到一个在定义时指定不包含`NULL`的列并且数据类型为整型或者字符串类型且列的定义不超过索引长度的最大值作为主键，如果找不到的话，会创建一个虚拟列作为该表的主键。

###  在定义表的时候定义索引

- 定义主键索引

  在`MySQL`中，当定义一个列为`PRIMARY KEY`的时候，就会将该列作为主键索引。

  ```sql
  #创建一个包含主键索引和唯一索引的表
  CREATE TABLE pindex (
  `ID` INT NOT NULL auto_increment,
  `UUID` varchar(64) NOT NULL,
  PRIMARY KEY(`ID`),
  UNIQUE (UUID)
  )
  ```

  如果表已经创建成功了，但是想添加主键索引可以使用下面的两种方法进行添加：

  ```sql
  #方法一  使用 ALTER TABLE 进行添加
  ALTER TABLE student ADD PRIMARY KEY (`ID`);
  ```

  

- 定义唯一索引
  在`MYSQL`中，定义一个唯一索引需要使用`UNIQUE`关键字。

  ```sql
  CREATE TABLE user_info(
    ID INT PRIMARY KEY auto_increment,
    username VARCHAR(50) NOT NULL UNIQUE, #创建唯一索引
    phone VARCHAR(11) NOT NULL,
    email VARCHAR(255),
    INDEX(email), #
    INDEX username_phone (username,phone) #创建联合索引
  );
  ```

- 定义普通索引
  定义普通索引只需要使用`INDEX(字段名)`即可。

- 定义联合索引
  定义联合索引也是使用INDEX关键字，只是需要指定多个字段，并且为该索引命名.

  ```sql
  INDEX username_phone (username,phone) #创建联合索引
  ```

  联合索引最多可以包含16列。
  联合索引遵循最左前缀原则，也就是说如果如果定义了一个联合索引`(a,b,c)`。

  以下查询是使用了联合索引：

  ```sql
  SELECT * FROM table_name WHERE a ="1";
  SELECT * FROM table_name WHERE a ="1" and b="2";
  SELECT * FROM table_name WHERE a ="1" and b="2" and c="3";
  SELECT * FROM table_name WHERE a ="1" and c="3";
  SELECT * FROM table_name WHERE a="1" and (b="2" or b="3")
  ...
  ```

  但是以下例子是不走联合索引的而是直接全表扫描：

  ```sql
  SELECT * FROM table_name WHERE b ="1";
  SELECT * FROM table_name WHERE c ="1";
  SELECT * FROM table_name WHERE a ="1" or b="2";
  ...
  ```

  主要原因是索引的底层是一个B+树，对于联合索引来说，这个B+树的节点存储的是（a,b,c），并且优先按照a字段的顺序排序，然后再按照b的顺序排序，然后再是c。如果直接使用b或c的话，由于b和c字段在索引数据结构中并不是有序的，只有当a相等时才可以有序找到，否则还不如直接全表扫描。

- 定义前缀索引
  也是使用INDEX关键字，只是在指定字段的时候，指定字段前缀长度。

  ```sql
  name varchar(50)
  INDEX(name(10)) #定义name的前10个字符为索引
  ```

  如果超过了指定的前缀长度，那么会将符合前缀长度数据通过索引获取到，剔除了不符合的数据，然后通过全表扫描获取相应的数据。

- 全文索引

  ```sql
  CREATE TABLE articles (
      id INT AUTO_INCREMENT PRIMARY KEY,
      title VARCHAR(200),
      content TEXT,
      FULLTEXT (title, content) -- 对标题和内容创建联合全文索引
  ) ENGINE=InnoDB;
  ```

  `FULLTEXT`索引采用了倒排索引技术，它会预先将文本拆分成一个个单词（分词），然后记录每个单词出现在哪一行，查询时直接匹配单词，速度很快。

  如果定义了全文索引 不能使用`LIKE`进行查询，只能通过特殊的语法：

  ```sql
  SELECT * FROM articles 
  WHERE MATCH(title, content) AGAINST('数据库 性能优化');
  ```

  并且全文索引字段类型只能是`CHAR`,`VARCHAR`,`TEXT`类型。

**存储引擎**：MySQL 5.6 之后，`InnoDB` 和 `MyISAM` 都支持。

**分词器（Stopwords）**：

- MySQL 默认不索引太短的词（通常是 3 个字符以下）。
- 它会过滤掉“停止词”（如 the, is, a 等高频但无意义的词）。

**中文分词**：

- **痛点**：英文靠空格分词，但中文是连在一起的。
- **方案**：MySQL 5.7 之后引入了 **ngram 分词器**。创建索引时必须指定： `ALTER TABLE articles ADD FULLTEXT (content) WITH PARSER ngram;` 如果不加这个，中文搜索通常会失效。

## 索引失效

接下来我么针对官方数据库的`sakila`数据库进行演示。

虽然我们为一些字段定了很多索引，但并不是每一次查询都是走索引，一些查询可能不走索引而是直接全表扫描。这样会十分耗时。

有关EXPLAIN工具的使用，可以参考这篇文章。[查看EXPLAIN文章]({{< ref "explain-tools.md" >}})

### 对索引字段做函数 / 运算操作

```sql
EXPLAIN SELECT * FROM actor WHERE last_name="DAVIS";
EXPLAIN SELECT * FROM actor WHERE CONCAT(last_name,"s")="DAVIS";
```

可以发现第一条指令，走了索引。

```sql
-> Index lookup on actor using idx_actor_last_name (last_name = 'DAVIS')  (cost=1.05 rows=3)
```

第二条指令，没有走索引，走了全表扫描。

```sql
-> Filter: (concat(actor.last_name,'s') = 'DAVIS')  (cost=21 rows=200)
    -> Table scan on actor  (cost=21 rows=200)

```

如果将函数或者运算放置到条件的另一侧（简单运算）可能不会导致索引失效。

```sql
EXPLAIN SELECT * FROM actor WHERE last_name=CONCAT("DAVI","s"); 
```

这个是走索引的。

解决方案： 在业务层就将要修改的内容进行处理。

### 模糊查询中通配符在开头

```sql
EXPLAIN  SELECT last_name FROM actor WHERE last_name LIKE"D%";
EXPLAIN  SELECT last_name FROM actor WHERE last_name LIKE"%D";
EXPLAIN  SELECT * FROM actor WHERE last_name LIKE"%D";
```

第一条指令走了索引，使用了覆盖索引并且进行了范围扫描。

```sql
-> Filter: (actor.last_name like 'D%')  (cost=4.57 rows=21)
    -> Covering index range scan on actor using idx_actor_last_name over ('D' <= last_name <= 'D????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????')  (cost=4.57 rows=21)
```

第二条指令虽然使用了通配符在开头，但是其只需要遍历整个二级索引树，并不需要回到主键索引中，依次遍历主键索引的叶子节点（数据量大，节点内容也大，慢）。

```sql
-> Filter: (actor.last_name like '%D')  (cost=20.2 rows=22.2)
    -> Covering index scan on actor using idx_actor_last_name  (cost=20.2 rows=200)
```

第三条指令由于需要返回所有符合的记录，所以需要遍历主键索引的叶子节点，挨个遍历，所以是全表扫描。速度慢。

```sql
-> Filter: (actor.last_name like '%D')  (cost=20.2 rows=22.2)
    -> Table scan on actor  (cost=20.2 rows=200)
```

然后我们具体分析以下第二条指令和第三条指令，具体执行的时间，可能有误差：

```sql
-> Filter: (actor.last_name like '%D')  (cost=20.2 rows=22.2) (actual time=0.104..0.165 rows=12 loops=1)
    -> Covering index scan on actor using idx_actor_last_name  (cost=20.2 rows=200) (actual time=0.0841..0.123 rows=200 loops=1)

-> Filter: (actor.last_name like '%D')  (cost=20.2 rows=22.2) (actual time=0.0235..0.0997 rows=12 loops=1)
    -> Table scan on actor  (cost=20.2 rows=200) (actual time=0.0183..0.0752 rows=200 loops=1)
```

由于数据样本太小，导致全表扫描速度比扫描整个二级索引文件还要快，并且也有可能因为运行环境问题导致的，多执行几次，发现全表扫描还是有可能比扫描整个二级索引文件要慢。下面我们找一个数据量大的表格进行重新测试。

```sql
USE world;
EXPLAIN ANALYZE SELECT CountryCode FROM city WHERE CountryCode LIKE "%U";
EXPLAIN ANALYZE SELECT * FROM city WHERE CountryCode LIKE "%U";
```

首先world数据库中的city表有4000+数据，而sakila中的actor只有200条数据。

```sql
# 第一条指令
-> Filter: (city.CountryCode like '%U')  (cost=410 rows=448) (actual time=0.0975..1.05 rows=143 loops=1)
    -> Covering index scan on city using CountryCode  (cost=410 rows=4035) (actual time=0.0641..0.688 rows=4079 loops=1)
    
    # 第二条指令
-> Filter: (city.CountryCode like '%U')  (cost=410 rows=448) (actual time=0.191..1.82 rows=143 loops=1)
    -> Table scan on city  (cost=410 rows=4035) (actual time=0.136..1.4 rows=4079 loops=1)

    
```

运行多次都会发现第二条指令执行的时间更长。

**解决方法**：

- 业务必须查后缀时，用全文索引（MySQL 5.6+ 支持）；


###  违背了最左匹配原则

这是联合索引失效最常见的原因。如果你创建了(a,b,c)联合索引，查询必须从`a`开始。不然会导致索引失效。

由于sakila中的数据较少，并且没有类似于（a,b,c）的联合索引。所以我自己创建了一个数据库和表。使用go语言插入了随机10000条数据。

```go
func InsertRecord(db *gorm.DB) {
	total := 10000
	users := make([]model.User, total)

	fmt.Println("正在准备 10,000 条数据...")
	for i := 0; i < total; i++ {
		users[i] = model.User{
			Username: fmt.Sprintf("user_%s", randomString(6)),
			Phone:    fmt.Sprintf("13%d%08d", rand.IntN(10), rand.IntN(100000000)),
			Email:    fmt.Sprintf("%s@example.com", randomString(8)),
		}
	}

	fmt.Println("开始批量插入数据库...")
	start := time.Now()

	// 使用 CreateInBatches，每批 1000 条
	err := db.CreateInBatches(users, 1000).Error

	if err != nil {
		fmt.Printf("插入失败: %v\n", err)
	} else {
		fmt.Printf("✅ 成功！耗时: %v\n", time.Since(start))
	}
}

// 辅助函数：生成随机字符串
func randomString(n int) string {
	var letters = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
	s := make([]rune, n)
	for i := range s {
		s[i] = letters[rand.IntN(len(letters))]
	}
	return string(s)
}

```

接下来我们验证联合索引失效的例子。

```sql
EXPLAIN ANALYZE SELECT *  FROM user WHERE username="user_iTnrfj" ;
EXPLAIN ANALYZE SELECT * FROM user WHERE phone="13755674698";
EXPLAIN ANALYZE SELECT * FROM user WHERE email="QofEbO7d@example.com";
# 这三条查询的是同一条记录
```

第一条符合最左前缀原则，所以使用了索引。并且使用了回表而不是直接使用覆盖索引。

```sql
-> Index lookup on user using idx_username_phone_email (username = 'user_iTnrfj')  (cost=0.35 rows=1) (actual time=0.0596..0.0661 rows=1 loops=1)

```

第二条与第三条都不符合最左前缀原则，所以采用了全表扫描。

```sql
-> Filter: (`user`.phone = '13755674698')  (cost=979 rows=955) (actual time=1.31..7.55 rows=1 loops=1)
    -> Table scan on user  (cost=979 rows=9546) (actual time=1.29..6.47 rows=10000 loops=1)
    
-> Filter: (`user`.email = 'QofEbO7d@example.com')  (cost=979 rows=955) (actual time=0.0507..6.66 rows=1 loops=1)
    -> Table scan on user  (cost=979 rows=9546) (actual time=0.0406..5.81 rows=10000 loops=1)
    
    
```

接下来我们再对比以下其它例子：

```sql
EXPLAIN ANALYZE SELECT *  FROM user WHERE username="user_iTnrfj" AND phone="13755674698" ; #(a,b)
EXPLAIN ANALYZE SELECT *  FROM user WHERE username="user_iTnrfj"  AND email="QofEbO7d@example.com" ; #(a,c)
EXPLAIN ANALYZE SELECT *  FROM user WHERE phone="13755674698"  AND email="QofEbO7d@example.com" ; #(b,c)
```

根据最左前缀原则，第一条和第二条 使用了联合索引。

```sql
-> Index lookup on user using idx_username_phone_email (username = 'user_iTnrfj', phone = '13755674698')  (cost=0.35 rows=1) (actual time=0.0405..0.0425 rows=1 loops=1)
-> Index lookup on user using idx_username_phone_email (username = 'user_iTnrfj'), with index condition: (`user`.email = 'QofEbO7d@example.com')  (cost=0.26 rows=1) (actual time=0.0222..0.0235 rows=1 loops=1)
```

但是第三条不符合最左前缀原则。

```sql
-> Filter: ((`user`.email = 'QofEbO7d@example.com') and (`user`.phone = '13755674698'))  (cost=979 rows=95.5) (actual time=0.0393..4.18 rows=1 loops=1)
    -> Table scan on user  (cost=979 rows=9546) (actual time=0.0315..3.53 rows=10000 loops=1)
```

**解决方法**：

- 严格遵循「最左前缀」，查询条件包含联合索引的最左字段；
- 若确实只需查后续字段，为该字段单独建索引。

### 隐式类型转换

如果一个类型，进行了类型转换，那么此时索引也失效。

```sql
EXPLAIN ANALYZE SELECT *  FROM user WHERE phone="13755674698" ;
EXPLAIN ANALYZE SELECT *  FROM user WHERE phone= 13755674698 ; #int类型转换成varchar类型
```

第一个肯定是走索引，只是走回表。

```sql
-> Index lookup on user using phone (phone = '13755674698')  (cost=0.35 rows=1) (actual time=0.0203..0.0219 rows=1 loops=1)
```

但是第二个隐式类型转换了，所以导致索引失效了。

```sql
-> Filter: (`user`.phone = 13755674698)  (cost=979 rows=955) (actual time=0.0657..4.38 rows=1 loops=1)
    -> Table scan on user  (cost=979 rows=9546) (actual time=0.0548..3.5 rows=10000 loops=1)
```

### 使用了不等于/NOT/<>

对索引字段使用了`!=`,`<>`,`NOT`等否定判断，优化器会大概率放弃索引，走全表扫描。（NULL值判断IS NOT NULL也会失效，IS NULL部分场景可用）

```sql
EXPLAIN ANALYZE SELECT *  FROM user WHERE id = 15 ;
EXPLAIN ANALYZE SELECT *  FROM user WHERE id != 15 ;
```

第一条直接使用主键索引进行查询，可以直接获取数据。

```sql
-> Rows fetched before execution  (cost=0..0 rows=1) (actual time=208e-6..208e-6 rows=1 loops=1)
```

第二条使用了索引的否定判断，理论上索引失效，但是优化器进行了优化，将非操作，变为了范围查询id <15 or id >15。

```sql
-> Filter: (`user`.id <> 15)  (cost=961 rows=4787) (actual time=0.345..5.37 rows=9999 loops=1)
    -> Index range scan on user using PRIMARY over (id < 15) OR (15 < id)  (cost=961 rows=4787) (actual time=0.342..4.65 rows=9999 loops=1)

```

那么我们再测试一个不是主键索引的非操作，看会发生什么：

```sql
EXPLAIN ANALYZE SELECT *  FROM user WHERE phone="13755674698" ;
EXPLAIN ANALYZE SELECT *  FROM user WHERE phone!="13755674698" ;
```

执行上述指令，我们发现，非主键索引执行非操作，是会导致索引失效的。

```sql
-> Filter: (`user`.phone <> '13755674698')  (cost=979 rows=7188) (actual time=0.684..5.6 rows=9999 loops=1)
    -> Table scan on user  (cost=979 rows=9546) (actual time=0.345..4.13 rows=10000 loops=1)
```

这里需要思考为什么主键索引会被优化，其它普通索引为什么不会被优化呢？

首先要知道，主键索引的叶子节点就存储了数据，并且其叶子节点是有序的，根据主键会进行排序。所以其执行范围查找会很快。但是普通二级索引呢，其需要会表操作，并且其不能通过主键索引的叶子节点范围查找，只能通过自己的叶子节点范围查找到主键，然后再次回表，此时优化器觉得这样做还不如全表扫描快。

### 使用OR连接了非索引字段

首先要知道OR代表着所有匹配的结果都返回，那么如果索引后面或者前面的非索引字段采用or，此时就算走了索引，但是还得全表扫描找到非索引字段，还不如直接进行全表扫描快呢。

```sql
EXPLAIN ANALYZE SELECT *  FROM user WHERE username="user_iTnrfj" or phone="13755674698";
EXPLAIN ANALYZE SELECT *  FROM user WHERE username="user_iTnrfj" or created_at="2026-02-28 01:11:36.10" ; #created_at不是索引
```

其中我们发现如果一个索引or一个索引，是可以走索引的，但是or一个非索引字段是不走索引的。

```sql
-> Filter: ((`user`.username = 'user_iTnrfj') or (`user`.phone = '13755674698'))  (cost=2.38 rows=2) (actual time=0.0362..0.0366 rows=1 loops=1)
    -> Sort-deduplicate by row ID  (cost=2.38 rows=2) (actual time=0.0347..0.0351 rows=1 loops=1)
        -> Index range scan on user using idx_username_phone_email over (username = 'user_iTnrfj')  (cost=0.36 rows=1) (actual time=0.0158..0.0179 rows=1 loops=1)
        -> Index range scan on user using phone over (phone = '13755674698')  (cost=1.07 rows=1) (actual time=0.00386..0.00459 rows=1 loops=1)
```

```sql
-> Filter: ((`user`.username = 'user_iTnrfj') or (`user`.created_at = TIMESTAMP'2026-02-28 01:11:36.1'))  (cost=979 rows=956) (actual time=0.0551..4.13 rows=1 loops=1)
    -> Table scan on user  (cost=979 rows=9546) (actual time=0.0287..2.96 rows=10000 loops=1)
```

**解决方法**：

- 给非索引字段建索引；
- 拆分查询后合并结果（UNION）；
- 业务允许时，改用 IN 或 AND（需调整逻辑）。

### 结果集过大

如果所要查询的结果占总数的比例过高，优化器会觉得还不如全表来的快。因为你需要进行回表操作，遍历多次主键索引这棵树，还不如全表扫描快呢。

**解决方法**：

- 增加过滤条件，缩小结果集（最推荐）；

**结论：索引失效的本质是优化器无法利用索引的有序性进行快速定位数据**






