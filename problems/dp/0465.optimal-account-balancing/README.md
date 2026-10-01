# 465. 最优账单平衡  [Hard]

> https://leetcode.cn/problems/optimal-account-balancing/

给你一个表示交易的数组 transactions ，其中 transactions[i] = [from_i, to_i, amount_i] 表示 ID = from_i 的人给 ID = to_i 的人共计 amount_i $ 。

请你计算并返回还清所有债务的最小交易笔数。

 

示例 1：**

```

**输入：**transactions = [[0,1,10],[2,0,5]]
**输出：**2
**解释：**
#0 给 #1 $10 。
#2 给 #0 $5 。
需要进行两笔交易。一种结清债务的方式是 #1 给 #0 和 #2 各 $5 。
```

示例 2：**

```

**输入：**transactions = [[0,1,10],[1,0,1],[1,2,5],[2,0,5]]
**输出：**1
**解释：**
#0 给 #1 $10 。
#1 给 #0 $1 。
#1 给 #2 $5 。
#2 给 #0 $5 。
因此，#1 只需要给 #0 $4 ，所有的债务即可还清。

```

 

**提示：**

	- 1 <= transactions.length <= 8

	- transactions[i].length == 3

	- 0 <= from_i, to_i < 12

	- from_i != to_i

	- 1 <= amount_i <= 100
