---
title: '下一个更大元素II'
date: '2026-03-03T18:34:35+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- 单调栈
- leetcode
- 算法
- 下一个更大元素
menu:
  sidebar:
    name: 下一个更大元素II
    identifier: leetcode503
    parent: monotonic-stack
    weight: 10
---


# leetcode 503下一个更大元素II

## 题目描述

[503. 下一个更大元素 II](https://leetcode.cn/problems/next-greater-element-ii/)

给定一个循环数组 `nums` （ `nums[nums.length - 1]` 的下一个元素是 `nums[0]` ），返回 *`nums` 中每个元素的 **下一个更大元素*** 。

数字 `x` 的 **下一个更大的元素** 是按数组遍历顺序，这个数字之后的第一个比它更大的数，这意味着你应该循环地搜索它的下一个更大的数。如果不存在，则输出 `-1` 。

 

**示例 1:**

```
输入: nums = [1,2,1]
输出: [2,-1,2]
解释: 第一个 1 的下一个更大的数是 2；
数字 2 找不到下一个更大的数； 
第二个 1 的下一个最大的数需要循环搜索，结果也是 2。
```

**示例 2:**

```
输入: nums = [1,2,3,4,3]
输出: [2,3,4,-1,4]
```

 

**提示:**

- `1 <= nums.length <= 104`
- `-109 <= nums[i] <= 109`



## 解题思路

首先根据题目描述，`nums`是一个循环数组，并且`nums`中的元素是可以重复的。

这样如果根据单调栈来解决这个问题，栈中存储的元素不能直接是元素本身，而应该存储元素的索引。

- 对于循环数组，可以遍历两次数组，然后对于下标取模。
- 对于找到下一个更大元素，采用单调栈。



```go
func nextGreaterElements(nums []int) []int {
	//处理边界
	n := len(nums)

	if n == 0 {
		return []int{}
	}

	ans := make([]int, n)
	//初始状态所有元素都没有找到下一个更大的元素
	for i := 0; i < len(ans); i++ {
		ans[i] = -1
	}

	var stack []int
	for i := 0; i < 2*n; i++ {
		curIdx := i % n

		for len(stack) > 0 && nums[stack[len(stack)-1]] < nums[curIdx] {
			topIdx := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			ans[topIdx] = nums[curIdx]
		}

		stack = append(stack, curIdx)
	}
	return ans
}
```

- 时间复杂度:$O(n)$
- 空间复杂度:$O(n)$