---
title: '移除掉K位数字'
date: '2026-03-03T21:50:04+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- 单调栈
- leetcode
- 移除k位数字
menu:
  sidebar:
    name: 移除掉K位数字
    identifier: leetcode402
    parent: monotonic-stack
    weight: 10
---

# leetcode 402 移除掉K位数字

## 题目描述

[402. 移掉 K 位数字](https://leetcode.cn/problems/remove-k-digits/)

给你一个以字符串表示的非负整数 `num` 和一个整数 `k` ，移除这个数中的 `k` 位数字，使得剩下的数字最小。请你以字符串形式返回这个最小的数字。

 

**示例 1 ：**

```
输入：num = "1432219", k = 3
输出："1219"
解释：移除掉三个数字 4, 3, 和 2 形成一个新的最小的数字 1219 。
```

**示例 2 ：**

```
输入：num = "10200", k = 1
输出："200"
解释：移掉首位的 1 剩下的数字为 200. 注意输出不能有任何前导零。
```

**示例 3 ：**

```
输入：num = "10", k = 2
输出："0"
解释：从原数字移除所有的数字，剩余为空就是 0 。
```

 

**提示：**

- `1 <= k <= num.length <= 105`
- `num` 仅由若干位数字（0 - 9）组成
- 除了 **0** 本身之外，`num` 不含任何前导零



## 解题思路

本题可以采用贪心+单调栈的思路。

贪心算法是求子问题最优，然后推导出整体最优的算法思想。

贪心策略： 从左向右遍历数组，如果发现当前数字比它左边小，则证明删除左边元素会使整体数值下降最快。

单调栈： 找到下一个比它小的元素。

如果遍历完数组，k>0,那么直接从栈中弹出k次，如果栈为空了，直接返回0。

```go
func removeKdigits(num string, k int) string {
	if len(num) == 0 || len(num) < k {
		return "0"
	}
	var stack []byte

	for i := 0; i < len(num); i++ {
		for k > 0 && len(stack) > 0 && stack[len(stack)-1] > num[i] {
			stack = stack[:len(stack)-1]
			k--
		}

		stack = append(stack, num[i])
	}

	for k > 0 && len(stack) > 0 {
		stack = stack[:len(stack)-1]
		k--
	}

	result := strings.TrimLeft(string(stack), "0")

	if result == "" {
		return "0"
	}
	return result
}
```

