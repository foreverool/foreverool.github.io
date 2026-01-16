---
title: Unnecessarty nested code
date: '2026-01-17T03:05:52+08:00'
weight: 2
menu:
  notes:
    name: Unnecessarty nested code
    identifier: 2-unnecessary-nested-code
    parent: code-and-project
    weight: 2
---
{{< note title="Unnecessary nested code" >}}
`Unnecessary nested code`中文： 不必要的嵌套代码

首先我们分析一个丑陋的例子：

```go
// 很丑陋的版本
func join(s1, s2 string, max int) (string, error) {
	if s1 == "" {
		return "", errors.New("s1 is empty")
	} else {
		if s2 == "" {
			return "", errors.New("s2 is empty")
		} else {
			concat, err := concatenate(s1, s2)
			if err != nil {
				return "", err
			} else {
				if len(concat) > max {
					return concat[:max], nil
				} else {
					return concat, nil
				}
			}
		}
	}
}

func concatenate(s1, s2 string) (string, error) {
	return s1 + s2, nil
}

```

这个例子虽然逻辑上是正确的，但是它涵盖了太多层次的if-else，导致代码阅读起来相对困难，你个良好的代码，是在大致阅读代码的时候就知道这段代码是什么意思，而不是需要一步一步的看。

对于上述代码的优化版本：

```go
// 自行先优化一下
func joinV2(s1, s2 string, max int) (string, error) {
	if s1 == "" || s2 == "" {
		return "", errors.New("s1 or s2 is empty")
	}

	concat, err := concatenate(s1, s2)
	if err != nil {
		return "", err
	}

	if len(concat) > max {
		return concat[:max], nil
	}

	return concat, nil

}

// 100 mistakes 书本中在不涉及改动部分功能下优化版本
func joinV3(s1, s2 string, max int) (string, error) {
	if s1 == "" {
		return "", errors.New("s1 is empty")
	}

	if s2 == "" {
		return "", errors.New("s2 is empty")
	}

	concat, err := concatenate(s1, s2)
	if err != nil {
		return "", err
	}

	if len(concat) > max {
		return concat[:max], nil
	}

	return concat, nil

}
```

一般来说函数所需的嵌套层次越多，就与但阅读和理解。

接下来我们来看一下，如何避免太多层次的`if-else`。

- 当一个if语句块返回时，我们应该在所有情况下省略else语句块。

- 当然也可以走一个相反的路径，比如说`if condition {return }`那么我们也可以将condition修改为`if !condition{//执行业务逻辑}else {return}。

- 尽可能将正常执行的代码，对齐到代码的左侧。

  我们分析一下糟糕版本的代码，发现正常执行的代码一直在右侧挪动，如果这个嵌套层次更深，那么正常执行的代码还要继续往右侧移动。所以说我们尽可能将正常执行的逻辑对齐到代码的左侧，这样在阅读代码的过程中，很轻易的知道这段代码到底是要做什么。

  {{< /note >}}