---
title: '中序遍历'
date: '2026-02-20T22:45:57+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- 算法
- 二叉树
- 中序遍历

menu:
  sidebar:
    name: 中序遍历
    identifier: in-order
    parent: dfs
    weight: 10
---


# 中序遍历

二叉树的中序遍历顺序为优先遍历左子树，然后再遍历根元素，之后遍历右子树。

左->中->右的遍历顺序。

{{< mermaid align="center">}}
graph TD
    A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
{{< /mermaid >}}

上述二叉树其中序遍历节点顺序为：


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
    class D,B visited
{{< /mermaid >}}

---
{{< mermaid align="center">}}
graph TD
	classDef visited fill:#9f9,stroke:#333,stroke-width:4px;
   	A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
    class D,B,E visited
{{< /mermaid >}}

---
{{< mermaid align="center">}}
graph TD
	classDef visited fill:#9f9,stroke:#333,stroke-width:4px;
   	A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
    class D,B,E,A visited
{{< /mermaid >}}

---
{{< mermaid align="center">}}
graph TD
	classDef visited fill:#9f9,stroke:#333,stroke-width:4px;
   	A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
    class D,B,E,A,C visited
{{< /mermaid >}}
## 递归实现中序遍历

```go
func InOrderTraversal(root *dfs.BinaryTreeNode) {
	if root == nil {
		return
	}

	// 先遍历左子树
	InOrderTraversal(root.Left)

	// 遍历根节点
	fmt.Println(root.Data)

	// 遍历右子树
	InOrderTraversal(root.Right)
}
```

测试代码如下：

```go
func TestInOrderTraversal(t *testing.T) {
	a := dfs.NewTreeNode(10)
	b := dfs.NewTreeNode(5)
	c := dfs.NewTreeNode(2)
	d := dfs.NewTreeNode(7)
	e := dfs.NewTreeNode(15)
	a.Left = b
	a.Right = e
	b.Left = c
	b.Right = d

	InOrderTraversal(a)
} // output: 2 5 7  10 15

```

## 迭代实现中序遍历

首先根据递归的思路我们知道，中序遍历是先遍历左子树，然后再遍历根节点，最后遍历右子树。

所以我们可以先将根节点的左子树的所有左节点压入到栈中，当遇到空的左节点的时候，我们就需要处理根节点，然后将根节点的右子树放入到栈中。


{{< mermaid align="center">}}
graph TD
classDef visited fill:#f96,stroke:#333,stroke-width:2px
	subgraph Tree [二叉树]
		A((10)) --> B((5))
    	A --> C((15))
    	B --> D((2))
    	B --> E((7))
    	D --> nil
    	D -->F((11))
	end
	subgraph Stack [栈]
	
		StackTop[10]
		Next1[5]
		Next2[2]
		Next2 --- Next1 --- StackTop
	end
	class StackTop,Next1,Next2 visited
    style StackTop fill:#f96,stroke:#333,stroke-width:2px
    style Stack fill:#eee,stroke-dasharray: 5 5
{{< /mermaid >}}

当遇到左节点为空的时候，我们就需要处理当前根节点，然后将当前根节点的右子树放入到栈中。接下来就是处理当前根节点的右子树。 符合左->根->右的遍历规则。


{{< mermaid align="center">}}
graph TD
classDef visited fill:#f96,stroke:#333,stroke-width:2px
	subgraph Tree [二叉树]
		A((10)) --> B((5))
    	A --> C((15))
    	B --> D((2))
    	B --> E((7))
    	D --> nil
    	D -->F((11))
	end
	subgraph Stack [栈]
	
		StackTop[10]
		Next1[5]
		Next2[11]
		Next2 --- Next1 --- StackTop
	end
	class StackTop,Next1,Next2 visited
    style StackTop fill:#f96,stroke:#333,stroke-width:2px
    style Stack fill:#eee,stroke-dasharray: 5 5
{{< /mermaid >}}

```go
func inorderTraversal(root *dfs.BinaryTreeNode) []int {
	if root == nil {
		return []int{}
	}

	result := []int{}
	stack := list.New()
	cur := root

	for cur != nil || stack.Len() > 0 {
		if cur != nil {
			stack.PushBack(cur)
			cur = cur.Left // 左
		} else {
			element := stack.Back()
			stack.Remove(element)
			ev := element.Value.(*dfs.BinaryTreeNode)
			result = append(result, ev.Data) //中
			cur = ev.Right                   //右
		}
	}
	return result
}
```

