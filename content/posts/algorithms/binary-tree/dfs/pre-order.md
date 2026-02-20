---
title: '前序遍历'
date: '2026-02-20T22:45:53+08:00'
hero: 
draft: false
description: ""
theme: Toha
tags:
- 算法
- 二叉树
- 前序遍历
menu:
  sidebar:
    name: 前序遍历
    identifier: pre-order
    parent: dfs
    weight: 10
---


# 前序遍历

前序遍历主要是指中间节点的遍历顺序，其遍历节点的顺序为 中->左->右。


{{< mermaid align="center">}}
graph TD
    A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
{{< /mermaid >}}

上述二叉树的前序遍历访问节点顺序：

---
{{< mermaid align="center">}}
graph TD
	classDef visited fill:#9f9,stroke:#333,stroke-width:4px;
   	A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
    class A visited
{{< /mermaid >}}

---
{{< mermaid align="center">}}
graph TD
	classDef visited fill:#9f9,stroke:#333,stroke-width:4px;
   	A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
    class A,B visited
{{< /mermaid >}}

---
{{< mermaid align="center">}}
graph TD
	classDef visited fill:#9f9,stroke:#333,stroke-width:4px;
   	A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
    class A,B,D visited
{{< /mermaid >}}

---
{{< mermaid align="center">}}
graph TD
	classDef visited fill:#9f9,stroke:#333,stroke-width:4px;
   	A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
    class A,B,D,E visited
{{< /mermaid >}}

---
{{< mermaid align="center">}}
graph TD
	classDef visited fill:#9f9,stroke:#333,stroke-width:4px;
   	A((10)) --> B((5))
    A --> C((15))
    B --> D((2))
    B --> E((7))
    class A,B,D,E,C visited
{{< /mermaid >}}

## 递归实现前序遍历

```go
func PreOrderTraversal(root *dfs.BinaryTreeNode) {
	if root == nil {
		return
	}
	// 先便利根节点
	fmt.Println(root.Data)
	// 然后遍历左子树
	PreOrderTraversal(root.Left)

	// 最后遍历右子树
	PreOrderTraversal(root.Right)
}

```

测试代码如下：

```go
func TestPreorderTraversal(t *testing.T) {
	a := dfs.NewTreeNode(10)
	b := dfs.NewTreeNode(5)
	c := dfs.NewTreeNode(2)
	d := dfs.NewTreeNode(7)
	e := dfs.NewTreeNode(15)
	a.Left = b
	a.Right = e
	b.Left = c
	b.Right = d

	PreOrderTraversal(a)
}

```

## 前序遍历的迭代实现

递归是可以通过栈来模拟的。所以如果想要把一个递归方法转变为迭代的方法可以使用栈来解决这个问题。

按照递归的流程，前序遍历是先访问根节点，然后再访问左子树，最后访问右子树。

但是栈一般是先进后出的一种数据结构，所以我们可以先将根节点加入到栈中，然后从栈中读取根节点，然后将根节点的右子树放入栈中，再放入左子树。这样我们再次读取栈中元素的时候，优先读取的是左子树。

---
{{< mermaid align="center">}}
graph TD
	subgraph Tree [二叉树]
		A((10)) --> B((5))
    	A --> C((15))
    	B --> D((2))
    	B --> E((7))
	end
	subgraph Stack [栈]
		StackTop[10]
	end
	style A fill:#f96,stroke:#333,stroke-width:2px
    style StackTop fill:#f96,stroke:#333,stroke-width:2px
    style Stack fill:#eee,stroke-dasharray: 5 5
{{< /mermaid >}}

从栈中弹出根节点，分别将根节点的右子树和左子树依次放入到栈中。

---
{{< mermaid align="center">}}
graph TD
	classDef visited fill:#f96,stroke:#333,stroke-width:2px
	subgraph Tree [二叉树]
		A((10)) --> B((5))
    	A --> C((15))
    	B --> D((2))
    	B --> E((7))
	end
	subgraph Stack [栈]
		StackTop[5]
		Next1[15]
		bottom
		StackTop --- Next1 --- bottom
	end
	class A,StackTop,Next1 visited
    style Stack fill:#eee,stroke-dasharray: 5 5
{{< /mermaid >}}

从栈顶弹出元素，并且打印，然后将该栈顶元素的右子树和左子树一次压入栈中，等等循环，直到栈为空即可。

---
{{< mermaid align="center">}}
graph TD
	classDef visited fill:#f96,stroke:#333,stroke-width:2px
	subgraph Tree [二叉树]
		A((10)) --> B((5))
    	A --> C((15))
    	B --> D((2))
    	B --> E((7))
	end
	subgraph Stack [栈]
		StackTop[2]
		Next1[7]
		Next2[15]
		bottom
		StackTop --- Next1 ---Next2 --- bottom
	end
	class A,B,StackTop,Next1 visited
    style Stack fill:#eee,stroke-dasharray: 5 5
{{< /mermaid >}}

```go
func PreOrderTraversalByIterator(root *dfs.BinaryTreeNode) {
	if root == nil {
		return
	}

	stack := list.New()
	stack.PushBack(root)
	for stack.Len() > 0 {
		element := stack.Back()
		ev := element.Value.(*dfs.BinaryTreeNode)
		stack.Remove(element)
		fmt.Println(ev.Data)
		left := ev.Left
		right := ev.Right
		if right != nil {
			stack.PushBack(right)
		}
		if left != nil {
			stack.PushBack(left)
		}
	}
}
```