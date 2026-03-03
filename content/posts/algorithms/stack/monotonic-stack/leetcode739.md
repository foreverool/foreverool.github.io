---
title: '每日温度'
date: '2026-03-03T18:34:42+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- 单调栈
- leetcode
- 算法
- 温度
menu:
  sidebar:
    name: 每日温度
    identifier: leetcode739
    parent: monotonic-stack
    weight: 10
---


# leetcode 739 每日温度

## 题目描述

[739. 每日温度](https://leetcode.cn/problems/daily-temperatures/)

给定一个整数数组 `temperatures` ，表示每天的温度，返回一个数组 `answer` ，其中 `answer[i]` 是指对于第 `i` 天，下一个更高温度出现在几天后。如果气温在这之后都不会升高，请在该位置用 `0` 来代替。



**示例 1:**

```
输入: temperatures = [73,74,75,71,69,72,76,73]
输出: [1,1,4,2,1,1,0,0]
```

**示例 2:**

```
输入: temperatures = [30,40,50,60]
输出: [1,1,1,0]
```

**示例 3:**

```
输入: temperatures = [30,60,90]
输出: [1,1,0]
```

 

**提示：**

- `1 <= temperatures.length <= 105`
- `30 <= temperatures[i] <= 100`

## 解题思路

这是一个典型的求下一个最大元素距离的问题。

所以使用单调栈，但是需要注意的是单调栈存储的内容是元素的位置。

```go
func dailyTemperatures(temperatures []int) []int {
	n := len(temperatures)

	if n == 0 {
		return []int{}
	}

	ans := make([]int, n)

	var stack []int

	for i := 0; i < n; i++ {

		for len(stack) > 0 && temperatures[stack[len(stack)-1]] < temperatures[i] {
			topIdx := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			ans[topIdx] = i - topIdx
		}

		stack = append(stack, i)
	}
	return ans
}
```

- 时间复杂度:$O(n)$
- 空间复杂度:$O(n)$

