# 252. 会议室  [Easy]

> https://leetcode.cn/problems/meeting-rooms/

给定一个会议时间安排的数组 intervals ，其中 intervals[i] = [start_i, end_i]。

一个人可以参加所有会议，只要没有两个会议的时间段重叠。在时间 t 结束的会议和在时间 t 开始的会议不重叠。

如果一个人能够参加这里面的全部会议，返回 true，否则返回 false。

 

**示例 1：**

```

**输入：**intervals = [[0,30],[5,10],[15,20]]
**输出**：false

```

**示例 2：**

```

**输入：**intervals = [[7,10],[2,4]]
**输出**：true

```

 

**提示：**

	- 0 <= intervals.length <= 10^4

	- intervals[i].length == 2

	- 0 <= start_i < end_i <= 10^6
