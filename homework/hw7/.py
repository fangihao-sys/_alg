"""
Title: C(n, k) 組合數計算：動態規劃 vs. 純遞迴效能對比
Description: 示範如何透過動態規劃（帕斯卡三角形）解決重複子問題，並與指數級複雜度的純遞迴進行效能比較。
"""

import time


# ==========================================
# 方法一：非動態規劃（純遞迴法）
# 原理：C(n, k) = C(n-1, k-1) + C(n-1, k)
# 缺點：會產生大量重複計算，時間複雜度高達 O(2^n)
# ==========================================
def combination_recursive(n: int, k: int) -> int:
  # 邊界條件
  if k == 0 or k == n:
    return 1
  if k > n or k < 0:
    return 0

  return combination_recursive(n - 1, k - 1) + combination_recursive(
      n - 1, k
  )


# ==========================================
# 方法二：動態規劃（空間優化版 / 帕斯卡三角形）
# 原理：由下而上 (Bottom-up) 遞推，利用一維滾動陣列儲存狀態
# 優點：消滅重複計算，時間複雜度 O(n * k)，空間複雜度 O(k)
# ==========================================
def combination_dp(n: int, k: int) -> int:
  if k < 0 or k > n:
    return 0
  if k == 0 or k == n:
    return 1

  # 組合數對稱性優化：C(n, k) = C(n, n-k)
  if k > n - k:
    k = n - k

  # 初始化一維 DP 陣列
  dp = [0] * (k + 1)
  dp[0] = 1

  for i in range(1, n + 1):
    # 倒序迴圈更新，避免覆蓋上一輪需要的數值
    for j in range(min(i, k), 0, -1):
      dp[j] = dp[j] + dp[j - 1]

  return dp[k]


# ==========================================
# 效能測試與主程式
# ==========================================
if __name__ == "__main__":
  # 測試數值（注意：純遞迴在 n 超過 30 後會非常慢）
  n, k = 28, 14

  print("=" * 45)
  print(f" 正在計算 C({n}, {k}) 組合數")
  print("=" * 45)

  # 1. 測試動態規劃效能
  start_time = time.time()
  ans_dp = combination_dp(n, k)
  dp_duration = time.time() - start_time
  print(f"[動態規劃] 結果: {ans_dp}")
  print(f"[動態規劃] 耗時: {dp_duration:.8f} 秒\n")

  # 2. 測試純遞迴效能
  print("正在執行純遞迴法（可能需要等待幾秒鐘）...")
  start_time = time.time()
  ans_rec = combination_recursive(n, k)
  rec_duration = time.time() - start_time
  print(f"[純遞迴法] 結果: {ans_rec}")
  print(f"[純遞迴法] 耗時: {rec_duration:.8f} 秒")
  print("=" * 45)

  # 3. 速度倍數比較
  if dp_duration > 0:
    speedup = rec_duration / dp_duration
    print(f" 結論：動態規劃比純遞迴快了約 {speedup:,.0f} 倍！")
  print("=" * 45)
