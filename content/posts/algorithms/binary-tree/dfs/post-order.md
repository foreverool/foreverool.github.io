---
title: '后续遍历'
date: '2026-02-20T22:46:02+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- 算法
- 二叉树
- 后序遍历
menu:
  sidebar:
    name: 后续遍历
    identifier: post-order
    parent: dfs
    weight: 10
---


# 后续遍历

后续遍历二叉树的节点顺序为 先遍历左子树，然后遍历右子树，最后遍历根节点。

左->右->根

{{< mermaid align="center">}}
graph TD
    A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
{{< /mermaid >}}

上述二叉树后续遍历的节点顺序为：

{{< mermaid align="center">}}
graph TD
	classDef visited fill:#9f9,stroke:#333,stroke-width:4px;
   	A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
    class D visited
{{< /mermaid >}}

---
{{< mermaid align="center">}}
graph TD
	classDef visited fill:#9f9,stroke:#333,stroke-width:4px;
   	A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
    class D,E visited
{{< /mermaid >}}

---
{{< mermaid align="center">}}
graph TD
	classDef visited fill:#9f9,stroke:#333,stroke-width:4px;
   	A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
    class D,E,B visited
{{< /mermaid >}}

---
{{< mermaid align="center">}}
graph TD
	classDef visited fill:#9f9,stroke:#333,stroke-width:4px;
   	A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
    class D,E,B,C visited
{{< /mermaid >}}

---
{{< mermaid align="center">}}
graph TD
	classDef visited fill:#9f9,stroke:#333,stroke-width:4px;
   	A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
    class D,E,B,C,A visited
{{< /mermaid >}}

## 后续遍历的递归实现

```go
func PostOrderTraversal(root *dfs.BinaryTreeNode) {
	// 基本条件
	if root == nil {
		return
	}

	// 先遍历左子树
	PostOrderTraversal(root.Left)

	// 再遍历右子树
	PostOrderTraversal(root.Right)

	// 最后遍历根节点
	fmt.Println(root.Data)
}
```

测试代码：

```go
func TestPostorderTraversal(t *testing.T) {
	a := dfs.NewTreeNode(10)
	b := dfs.NewTreeNode(5)
	c := dfs.NewTreeNode(2)
	d := dfs.NewTreeNode(7)
	e := dfs.NewTreeNode(15)
	a.Left = b
	a.Right = e
	b.Left = c
	b.Right = d

	PostOrderTraversal(a)
} //output: 2 7 5 15 10

```

## 后续遍历的迭代实现

首先后续遍历的顺序为左->右->根，而前序遍历的顺序为根->左->右。我们只需要将前序遍历的变为根->右->左，然后将结果反转即可。

```go
func postorderTraversal(root *dfs.BinaryTreeNode) []int {
	if root == nil {
		return []int{}
	}

	result := []int{}
	stack := list.New()

	stack.PushBack(root)
	for stack.Len() > 0 {
		element := stack.Back()
		stack.Remove(element)
		ev := element.Value.(*dfs.BinaryTreeNode)
		result = append(result, ev.Data)
		if ev.Left != nil {
			stack.PushBack(ev.Left)
		}
		if ev.Right != nil {
			stack.PushBack(ev.Right)
		}
	}

	slices.Reverse(result)
	return result
}
```

