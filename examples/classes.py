"""類別、實例變數、繼承與覆寫。執行：python -m examples.classes"""


class Animal:
    """將動物的資料和行為放在同一個類別。"""

    species = "animal"  # 類別屬性：同類實例共享此預設字串。

    def __init__(self, name: str) -> None:
        if not isinstance(name, str):
            raise TypeError("名字必須是字串")
        if not name.strip():
            raise ValueError("名字不能留空")
        self.name = name
        # 必須在 __init__ 裡建立，讓每個實例擁有各自的 list。
        self.tricks: list[str] = []

    def add_trick(self, trick: str) -> None:
        if not isinstance(trick, str):
            raise TypeError("技能必須是字串")
        if not trick.strip():
            raise ValueError("技能不能留空")
        self.tricks.append(trick)

    def talk(self) -> str:
        return "..."

    def describe(self) -> str:
        return f"{self.name} ({self.species})：{self.talk()}"


class Dog(Animal):
    species = "dog"

    def talk(self) -> str:
        """覆寫父類別的 talk()。"""
        return "woof"


class Cat(Animal):
    species = "cat"

    def talk(self) -> str:
        return "meow"


def main() -> None:
    first_dog = Dog("小白")
    second_dog = Dog("小黑")
    cat = Cat("小橘")
    first_dog.add_trick("roll over")
    second_dog.add_trick("play dead")
    cat.add_trick("high five")

    print("每個實例都有自己的技能串列：")
    print(first_dog.name, first_dog.tricks)
    print(second_dog.name, second_dog.tricks)
    print(cat.name, cat.tricks)
    print("兩隻狗共用同一個串列嗎？", first_dog.tricks is second_dog.tricks)

    print("繼承：Dog 是 Animal 嗎？", isinstance(first_dog, Animal))
    print("多型：相同的 talk() 呼叫，依物件類別得到不同結果。")
    for animal in [first_dog, second_dog, cat]:
        print(animal.describe())


if __name__ == "__main__":
    main()
