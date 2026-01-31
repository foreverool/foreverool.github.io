---
title: 'database/sql中的Open函数'
date: '2026-01-30T22:34:41+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
  - go
  - sql
  - database

menu:
  sidebar:
    name: database/sql中的Open函数
    identifier: open-and-ping
    parent: go-sql
    weight: 1
---

# Go database/sql 中的Open函数与Ping函数

在`Go`语言中可以使用标准库`database/sql`进行连接数据库，其是`Go`官方提供的数据库操作通用抽象层，同样也是连接池管理器，它不直接实现任何数据库操作逻辑，也不依赖任何具体数据库，而是定义了一套所有数据库都能遵守的标准接口。比如：连接、执行SQL、获取结构等。

标准库的`sql`也实现了通用的连接池管理、并发安全、语句预处理等核心能力。

简单说`database/sql`核心作用是：

- 统一接口：让开发者用一套代码操作MySQL、PostgreSQL、SQLite等所有数据库，无需关心不同数据库底层差异。
-  封装了通用能力：把链接池、并发、错误处理等通用逻辑封装好，开发者无需重复造轮子。
- 解耦上层代码与底层数据库： 上层业务代码只依赖`database/sql`的标准接口，切换数据库时只需要替换驱动，无需修改业务代码。

​	关键点是：**database/sql**不是实际操作的，真正与数据库打交道的是驱动。

在使用标准库连接数据库之前，必须先在项目中安装具体数据库的驱动。

```shell
go get github.com/go-sql-driver/mysql
```

操作`MySQL`的核心流程：

**创建连接池**

```go
// 创建sql 连接池
func CreateDB(dsn string) (*sql.DB, error) {
	// 创建连接池
	pool, err := sql.Open("mysql", dsn)
	if err != nil {
		return nil, err
	}
	//配置连接池参数
	pool.SetMaxOpenConns(20)                   //连接池最大打开的连接数
	pool.SetMaxIdleConns(10)                   // 连接池最大空闲连接数
	pool.SetConnMaxLifetime(300 * time.Second) //连接最大存活时间
	pool.SetConnMaxIdleTime(60 * time.Second)  // 连接最大空闲时间

	return pool, nil
}

```

分析上述代码：

```go
func Open(driverName, dataSourceName string) (*DB, error) 
// driverName 标识驱动的名称 例如：mysql
// dsn 为data source name , 例如MySQL dsn格式为: <username>:<password>@<host>/<dbname>?value1=xxx&value2=xxx...
// 该Open函数返回一个连接池
```

DB连接池

```go
// DB is a database handle representing a pool of zero or more
// underlying connections. It's safe for concurrent use by multiple
// goroutines.
//
// The sql package creates and frees connections automatically; it
// also maintains a free pool of idle connections. If the database has
// a concept of per-connection state, such state can be reliably observed
// within a transaction ([Tx]) or connection ([Conn]). Once [DB.Begin] is called, the
// returned [Tx] is bound to a single connection. Once [Tx.Commit] or
// [Tx.Rollback] is called on the transaction, that transaction's
// connection is returned to [DB]'s idle connection pool. The pool size
// can be controlled with [DB.SetMaxIdleConns].
type DB struct {
	// Total time waited for new connections.
	waitDuration atomic.Int64

	connector driver.Connector
	// numClosed is an atomic counter which represents a total number of
	// closed connections. Stmt.openStmt checks it before cleaning closed
	// connections in Stmt.css.
	numClosed atomic.Uint64

	mu           sync.Mutex    // protects following fields
	freeConn     []*driverConn // free connections ordered by returnedAt oldest to newest
	connRequests connRequestSet
	numOpen      int // number of opened and pending open connections
	// Used to signal the need for new connections
	// a goroutine running connectionOpener() reads on this chan and
	// maybeOpenNewConnections sends on the chan (one send per needed connection)
	// It is closed during db.Close(). The close tells the connectionOpener
	// goroutine to exit.
	openerCh          chan struct{}
	closed            bool
	dep               map[finalCloser]depSet
	lastPut           map[*driverConn]string // stacktrace of last conn's put; debug only
	maxIdleCount      int                    // zero means defaultMaxIdleConns; negative means 0
	maxOpen           int                    // <= 0 means unlimited
	maxLifetime       time.Duration          // maximum amount of time a connection may be reused
	maxIdleTime       time.Duration          // maximum amount of time a connection may be idle before being closed
	cleanerCh         chan struct{}
	waitCount         int64 // Total number of connections waited for.
	maxIdleClosed     int64 // Total number of connections closed due to idle count.
	maxIdleTimeClosed int64 // Total number of connections closed due to idle time.
	maxLifetimeClosed int64 // Total number of connections closed due to max connection lifetime limit.

	stop func() // stop cancels the connection opener.
}
```

执行完`CreateDB`函数，它仅仅只是创建连接池，并没有与`MySQL`进行`tcp`三次握手

```go
	t.Run("wrong dsn", func(t *testing.T) {

		wrongDSN := "foreverool:wrongpassword@tcp(127.0.0.1)/study_mysql"
		pool, err := CreateDB(wrongDSN)
		if err != nil {
			panic(fmt.Sprintf("数据库连接失败：%v", err))
		}

		_ = pool

	})
```

上述例子我们传递了错误的`MySQL`账户密码，但是使用`sql.Open`函数并没有返回任何错误，进而验证了该函数仅仅只是创建连接池而不进行`MySQL`连接。

**`MySQL`采用懒加载的方式： 只有在真正需要使用连接时，才会发起网络连接，也就是说再第一次执行SQL的时候才会进行认证**

​	这就引出了一个问题，我们的项目都部署了，当我们执行SQL的时候才发现出错了，这样做导致程序的鲁棒性很差，最好的解决方案是，再创建好连接池之后，进行Ping。

​	如果`Ping()`没有返回任何错误，那么意味着我们的连接是正常建立的，如果返回了错误，那么我们可以在程序运行最开始就可以发现该问题，而不是在程序运行一段时间了，有数据库请求操作的时候才发现问题。

对之前代码的改进：

```GO
// 创建sql 连接池
func CreateDB(dsn string) (*sql.DB, error) {
	// 创建连接池
	pool, err := sql.Open("mysql", dsn)
	if err != nil {
		return nil, err
	}
	//配置连接池参数
	pool.SetMaxOpenConns(20)                   //连接池最大打开的连接数
	pool.SetMaxIdleConns(10)                   // 连接池最大空闲连接数
	pool.SetConnMaxLifetime(300 * time.Second) //连接最大存活时间
	pool.SetConnMaxIdleTime(60 * time.Second)  // 连接最大空闲时间

	err = pool.Ping()
	if err != nil {
		pool.Close() //如果连接失败必须手动释放pool 不然造成了太多连接池浪费
		return nil, err
	}

	return pool, nil
}

```