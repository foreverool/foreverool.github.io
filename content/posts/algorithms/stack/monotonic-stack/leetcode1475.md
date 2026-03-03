---
title: '商品折扣后的价格'
date: '2026-03-03T18:34:48+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- 单调栈
- leetcode
- 算法
- 商品折扣
menu:
  sidebar:
    name: 商品折扣后的价格
    identifier: leetcode1475
    parent: monotonic-stack
    weight: 10
---


# leetcode 1475 商品折扣后的最终价格

## 题目描述

[1475. 商品折扣后的最终价格](https://leetcode.cn/problems/final-prices-with-a-special-discount-in-a-shop/)

给你一个数组 `prices` ，其中 `prices[i]` 是商店里第 `i` 件商品的价格。

商店里正在进行促销活动，如果你要买第 `i` 件商品，那么你可以得到与 `prices[j]` 相等的折扣，其中 `j` 是满足 `j > i` 且 `prices[j] <= prices[i]` 的 **最小下标** ，如果没有满足条件的 `j` ，你将没有任何折扣。

请你返回一个数组，数组中第 `i` 个元素是折扣后你购买商品 `i` 最终需要支付的价格。

 

**示例 1：**

```
输入：prices = [8,4,6,2,3]
输出：[4,2,4,2,3]
解释：
商品 0 的价格为 price[0]=8 ，你将得到 prices[1]=4 的折扣，所以最终价格为 8 - 4 = 4 。
商品 1 的价格为 price[1]=4 ，你将得到 prices[3]=2 的折扣，所以最终价格为 4 - 2 = 2 。
商品 2 的价格为 price[2]=6 ，你将得到 prices[3]=2 的折扣，所以最终价格为 6 - 2 = 4 。
商品 3 和 4 都没有折扣。
```

**示例 2：**

```
输入：prices = [1,2,3,4,5]
输出：[1,2,3,4,5]
解释：在这个例子中，所有商品都没有折扣。
```

**示例 3：**

```
输入：prices = [10,1,1,6]
输出：[9,0,1,6]
```

 

**提示：**

- `1 <= prices.length <= 500`
- `1 <= prices[i] <= 10^3`



## 解题思路

这道题 本质上就是找到i之后的元素比它小的元素，那么就可以使用单调递增栈来解决。

只要找到下一个比它小的元素，那么直接返回栈顶元素的价格-当前元素价格。

```go
func finalPrices(prices []int) []int {
	n := len(prices)

	if n == 0 {
		return []int{}
	}

	//如果没有找到比它小的元素，只能返回原来的价格
	ans := make([]int, n)
	copy(ans, prices)

	var stack []int

	for i := 0; i < n; i++ {

		for len(stack) > 0 && prices[stack[len(stack)-1]] >= prices[i] {
			topIdx := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			ans[topIdx] -= prices[i]
		}

		stack = append(stack, i)
	}
	return ans
}

```

- 时间复杂度:$O(n)$
- 空间复杂度:$O(n)$