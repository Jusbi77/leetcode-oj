# 1100. 长度为 K 的无重复字符子串  [Medium]

> https://leetcode.cn/problems/find-k-length-substrings-with-no-repeated-characters/

给你一个字符串 s，找出所有长度为 k 且不含重复字符的子串，请你返回全部满足要求的子串的 **数目**。

 

**示例 1：**

```

**输入：**s = "havefunonleetcode", k = 5
**输出：**6
**解释：**
这里有 6 个满足题意的子串，分别是：'havef','avefu','vefun','efuno','etcod','tcode'。

```

**示例 2：**

```

**输入：**s = "home", k = 5
**输出：**0
**解释：**
注意：k 可能会大于 s 的长度。在这种情况下，就无法找到任何长度为 k 的子串。
```

 

**提示：**

	- 1 <= s.length <= 10^4

	- s 中的所有字符均为小写英文字母

	- 1 <= k <= 10^4
