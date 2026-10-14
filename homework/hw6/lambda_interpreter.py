# -*- coding: utf-8 -*-
"""
Lambda Calculus Interpreter with Step-by-Step Reduction Trace
Author: Gemini Collaborator
Language: Python 3
"""

import re

# ==========================================
# 1. AST (Abstract Syntax Tree) 定義
# ==========================================

class Expr:
    pass

class Var(Expr):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

class Abs(Expr):
    def __init__(self, param, body):
        self.param = param
        self.body = body
    def __repr__(self):
        return f"(\\{self.param}. {self.body})"

class App(Expr):
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg
    def __repr__(self):
        # 加上括號以保持可讀性
        func_str = f"({self.func})" if isinstance(self.func, Abs) else str(self.func)
        arg_str = f"({self.arg})" if isinstance(self.arg, (Abs, App)) else str(self.arg)
        return f"{func_str} {arg_str}"

# ==========================================
# 2. 輔助函數：自由變數與安全代換 (Capture-Avoiding Substitution)
# ==========================================

def free_vars(expr):
    """計算運算式中的自由變數集合"""
    if isinstance(expr, Var):
        return {expr.name}
    elif isinstance(expr, Abs):
        return free_vars(expr.body) - {expr.param}
    elif isinstance(expr, App):
        return free_vars(expr.func) | free_vars(expr.arg)
    return set()

def fresh_var(base_name, existing_vars):
    """產生一個不衝突的新變數名稱（Alpha 轉換用）"""
    if base_name not in existing_vars:
        return base_name
    i = 1
    while f"{base_name}_{i}" in existing_vars:
        i += 1
    return f"{base_name}_{i}"

def substitute(expr, var_name, replacement):
    """將 expr 中所有自由的 var_name 替換為 replacement（避免變數捕捉）"""
    if isinstance(expr, Var):
        return replacement if expr.name == var_name else expr
    elif isinstance(expr, Abs):
        if expr.param == var_name:
            return expr  # 變數被遮蔽 (shadowed)
        fvs_repl = free_vars(replacement)
        if expr.param in fvs_repl:
            # 發生變數衝突，進行 Alpha 轉換
            all_fvs = free_vars(expr.body) | fvs_repl | {var_name}
            new_param = fresh_var(expr.param, all_fvs)
            new_body = substitute(expr.body, expr.param, Var(new_param))
            return Abs(new_param, substitute(new_body, var_name, replacement))
        else:
            return Abs(expr.param, substitute(expr.body, var_name, replacement))
    elif isinstance(expr, App):
        return App(substitute(expr.func, var_name, replacement),
                   substitute(expr.arg, var_name, replacement))
    return expr

# ==========================================
# 3. 語法解析器 (Lexer & Parser)
# ==========================================

class Lexer:
    def __init__(self, text):
        # 抓取 \, ., (, ), 以及變數名稱
        self.tokens = re.findall(r'\\|\.|\(|\)|[a-zA-Z_][a-zA-Z0-9_]*', text)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        tok = self.peek()
        self.pos += 1
        return tok

class Parser:
    def __init__(self, text):
        self.lexer = Lexer(text)

    def parse(self):
        expr = self.parse_expr()
        if self.lexer.peek() is not None:
            raise SyntaxError(f"未預期的詞彙: {self.lexer.peek()}")
        return expr

    def parse_expr(self):
        if self.lexer.peek() == '\\':
            self.lexer.consume()  # 吃掉 '\'
            param = self.lexer.consume()
            if not param or not re.match(r'^[a-zA-Z_]', param):
                raise SyntaxError("期望在 '\\' 後方得到參數名稱")
            dot = self.lexer.consume()
            if dot != '.':
                raise SyntaxError("期望在參數後方得到 '.'")
            body = self.parse_expr()
            return Abs(param, body)
        else:
            return self.parse_app()

    def parse_app(self):
        left = self.parse_atom()
        while True:
            nxt = self.lexer.peek()
            if nxt is None or nxt in (')', '.'):
                break
            right = self.parse_atom()
            left = App(left, right)
        return left

    def parse_atom(self):
        tok = self.lexer.peek()
        if tok == '(':
            self.lexer.consume()
            expr = self.parse_expr()
            close = self.lexer.consume()
            if close != ')':
                raise SyntaxError("缺少右括號 ')'")
            return expr
        elif tok and re.match(r'^[a-zA-Z_]', tok):
            self.lexer.consume()
            return Var(tok)
        else:
            raise SyntaxError(f"未預期的詞彙: {tok}")

# ==========================================
# 4. 正規序規約引擎 (Normal-Order Reduction)
# ==========================================

def reduce_step(expr):
    """執行單步規約。回傳 (新運算式, 是否成功規約, 步驟描述)"""
    if isinstance(expr, Var):
        return expr, False, ""
    elif isinstance(expr, Abs):
        new_body, did, desc = reduce_step(expr.body)
        if did:
            return Abs(expr.param, new_body), True, desc
        return expr, False, ""
    elif isinstance(expr, App):
        # 1. 如果左側是抽象，直接進行 Beta 規約
        if isinstance(expr.func, Abs):
            param = expr.func.param
            body = expr.func.body
            arg = expr.arg
            res = substitute(body, param, arg)
            desc = f"Beta 規約: 將 ({expr.func}) 套用到 ({arg})，代換變數 '{param}'"
            return res, True, desc
        
        # 2. 否則按照正規序先規約左側函數
        new_func, did_func, desc_func = reduce_step(expr.func)
        if did_func:
            return App(new_func, expr.arg), True, desc_func
        
        # 3. 左側無法規約，則規約右側參數
        new_arg, did_arg, desc_arg = reduce_step(expr.arg)
        if did_arg:
            return App(expr.func, new_arg), True, desc_arg
            
        return expr, False, ""

def evaluate(expr, max_steps=50):
    """完整評估運算式並印出詳細步驟"""
    current = expr
    print(f"初始運算式: {current}")
    print("-" * 50)
    
    step = 0
    while step < max_steps:
        next_expr, reduced, description = reduce_step(current)
        if not reduced:
            print("-" * 50)
            print(f"達到正常形 (Normal Form): {current}")
            break
        
        step += 1
        print(f"步驟 {step}: {description}")
        print(f"  => {next_expr}")
        current = next_expr
    else:
        print("警告: 達到最大計算步數限制，可能為非終止迴圈。")
    print("=" * 50 + "\n")

# ==========================================
# 5. 測試案例 (Test Programs)
# ==========================================

if __name__ == "__main__":
    print("=== Lambda Calculus 逐步解譯器測試 ===\n")

    # 測試 1: 簡單的身份函數應用
    # (\x. x) y
    code1 = "(\\x. x) y"
    print(f"測試 1: {code1}")
    evaluate(Parser(code1).parse())

    # 測試 2: 函數代換與巢狀應用
    # (\x. \y. x y) a b
    code2 = "(\\x. \\y. x y) a b"
    print(f"測試 2: {code2}")
    evaluate(Parser(code2).parse())

    # 測試 3: 邱奇數 (Church Numerals) - 數字 1 加到 2 的概念 (或簡單應用)
    # 這裡測試 Church 函數套用: (\f. \x. f (f x)) (\y. y) z
    code3 = "(\\f. \\x. f (f x)) (\\y. y) z"
    print(f"測試 3: {code3}")
    evaluate(Parser(code3).parse())
