"""基礎語法與函式練習。執行：python -m examples.basics"""

import argparse


def _check_non_negative_integer(value: int) -> None:
    """排除小數、字串、布林值與負數。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("n 必須是整數")
    if value < 0:
        raise ValueError("n 必須大於或等於 0")


def factorial(n: int) -> int:
    """計算 n!，其中 0! = 1。迴圈版本不需要遞迴呼叫。"""
    _check_non_negative_integer(n)
    result = 1
    for number in range(1, n + 1):
        result *= number
    return result


def fibonacci(n: int) -> int:
    """回傳第 n 個費氏數；F(0) = 0，F(1) = 1。"""
    _check_non_negative_integer(n)
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


def factorial_recursive(n: int) -> int:
    """教學用遞迴版本。限制 n <= 100，避免過深的函式呼叫。"""
    _check_non_negative_integer(n)
    if n > 100:
        raise ValueError("遞迴示範請使用 0 到 100；較大的 n 請用 factorial()")

    def calculate(number: int) -> int:
        if number == 0:
            return 1
        return number * calculate(number - 1)

    return calculate(n)


def fibonacci_recursive(n: int) -> int:
    """教學用遞迴版本。重複運算很多，故限制 n <= 20。"""
    _check_non_negative_integer(n)
    if n > 20:
        raise ValueError("遞迴示範請使用 0 到 20；較大的 n 請用 fibonacci()")

    def calculate(number: int) -> int:
        if number < 2:
            return number
        return calculate(number - 1) + calculate(number - 2)

    return calculate(n)


def _demo_number(text: str) -> int:
    """argparse 的輸入驗證：命令列輸入與 input() 一樣先是字串。"""
    try:
        number = int(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("請輸入整數，例如 6") from error
    if not 0 <= number <= 100:
        raise argparse.ArgumentTypeError("示範數字請使用 0 到 100")
    return number


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Python 基礎語法、階乘與費氏數列")
    parser.add_argument("--number", type=_demo_number, default=6, help="示範用的整數，0 到 100（預設：6）")
    args = parser.parse_args(argv)

    name = "Python"
    price = 12.5
    ready = True
    print(f"字串：{name}；浮點數：{price}；布林值：{ready}")
    print("型別：", type(name).__name__, type(price).__name__, type(ready).__name__)
    print("跳脫字元：第一行\n第二行\t有一個 Tab")
    print("自訂分隔符號", "A", "B", sep=" | ")

    total = 10
    total += 3
    print(f"10 += 3 → {total}；13 / 5 = {total / 5}")
    print(f"13 // 5 = {total // 5}；13 % 5 = {total % 5}；2 ** 3 = {2 ** 3}")

    score = 85
    if score >= 90:
        grade = "優等"
    elif score >= 60:
        grade = "及格"
    else:
        grade = "再加油"
    print(f"條件判斷：{score} 分 → {grade}")
    print(f"邏輯判斷：ready and score >= 60 → {ready and score >= 60}")
    print("for / range：", list(range(1, 6)))

    countdown = 3
    while countdown > 0:
        print(f"while 倒數：{countdown}")
        countdown -= 1  # 改變條件，讓迴圈可以結束。

    n = args.number
    print(f"{n}! = {factorial(n)}")
    print(f"F({n}) = {fibonacci(n)}")
    print("前 10 個費氏數：", [fibonacci(index) for index in range(10)])
    # 遞迴教學固定使用小數字，執行時間不會隨命令列參數爆增。
    print(f"遞迴示範：6! = {factorial_recursive(6)}；F(6) = {fibonacci_recursive(6)}")


if __name__ == "__main__":
    main()
