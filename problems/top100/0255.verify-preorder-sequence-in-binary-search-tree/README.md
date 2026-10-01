# 255. 验证二叉搜索树的前序遍历序列  [Medium]

> https://leetcode.cn/problems/verify-preorder-sequence-in-binary-search-tree/

给定一个 **无重复元素** 的整数数组 preorder ， 如果它是以二叉搜索树的**先序遍历**排列 ，返回 true 。

 

**示例 1：**

```

**输入: **preorder = [5,2,1,3,6]
**输出: **true
```

**示例 2：**

```

**输入: **preorder = [5,2,6,1,3]
**输出: **false
```

 

**提示:**

	- 1 <= preorder.length <= 10^4

	- 1 <= preorder[i] <= 10^4

	- preorder 中 **无重复元素**

 

**进阶：**您能否使用恒定的空间复杂度来完成此题？
