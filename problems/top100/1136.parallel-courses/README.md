# 1136. 并行课程  [Medium]

> https://leetcode.cn/problems/parallel-courses/

给你一个整数 n ，表示编号从 1 到 n 的 n 门课程。另给你一个数组 relations ，其中 relations[i] = [prevCourse_i, nextCourse_i] ，表示课程 prevCourse_i 和课程 nextCourse_i 之间存在先修关系：课程 prevCourse_i 必须在 nextCourse_i 之前修读完成。

在一个学期内，你可以学习 **任意数量** 的课程，但前提是你已经在 **上** 一学期修读完待学习课程的所有先修课程。

请你返回学完全部课程所需的 **最少** 学期数。如果没有办法做到学完全部这些课程的话，就返回 -1。

 

 

示例 1：**

```

**输入：**n = 3, relations = [[1,3],[2,3]]
**输出：**2
**解释：**上图表示课程之间的关系图：
在第一学期，可以修读课程 1 和 2 。
在第二学期，可以修读课程 3 。

```

示例 2：**

```

**输入：**n = 3, relations = [[1,2],[2,3],[3,1]]
**输出：**-1
**解释：**没有课程可以学习，因为它们互为先修课程。

```

 

**提示：**

	- 1 <= n <= 5000

	- 1 <= relations.length <= 5000

	- relations[i].length == 2

	- 1 <= prevCourse_i, nextCourse_i <= n

	- prevCourse_i != nextCourse_i

	- 所有 [prevCourse_i, nextCourse_i] **互不相同**
