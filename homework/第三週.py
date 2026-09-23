使用chatgpt做的

from itertools import product


def solve_sat(clauses):
    """
    使用 Brute Force 求解 SAT 問題

    clauses 格式：
    [
        [('A', True), ('B', False)],
        [('B', True), ('C', True)],
        [('A', False), ('C', False)]
    ]

    True  = 正文字面，例如 A
    False = 負文字面，例如 ¬A
    """

    # 找出所有變數
    variables = set()

    for clause in clauses:
        for var, _ in clause:
            variables.add(var)

    variables = sorted(variables)

    # 窮舉所有可能的 True / False 組合
    for values in product([False, True], repeat=len(variables)):

        assignment = dict(zip(variables, values))

        # 檢查每一個 clause
        all_clauses_true = True

        for clause in clauses:
            clause_true = False

            # Clause 裡只要有一個 literal 為 True 即可
            for var, positive in clause:

                value = assignment[var]

                if positive and value:
                    clause_true = True
                    break

                if not positive and not value:
                    clause_true = True
                    break

            # 如果有任何一個 clause 不成立
            if not clause_true:
                all_clauses_true = False
                break

        # 所有 clause 都成立
        if all_clauses_true:
            return assignment

    # 找不到解
    return None


# =========================
# 測試 SAT 問題
# =========================

# (A OR NOT B)
# AND
# (B OR C)
# AND
# (NOT A OR NOT C)

clauses = [
    [('A', True), ('B', False)],
    [('B', True), ('C', True)],
    [('A', False), ('C', False)]
]


solution = solve_sat(clauses)


if solution:
    print("SAT：找到滿足解")
    print(solution)
else:
    print("UNSAT：不存在滿足解")
