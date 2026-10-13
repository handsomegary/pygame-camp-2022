"""容器、字串轉換與 import 練習。執行：python -m examples.containers"""

import math
import random


def build_demo(seed: int = 2022) -> dict:
    """建立練習結果；固定亂數種子，方便比較每次執行的輸出。"""
    fruits = ["apple", "banana"]
    fruits.append("orange")  # 加入一個元素。
    fruits.insert(1, "grape")  # 放在索引 1。
    fruits.extend(["pear", "melon"])  # 加入另一個容器的元素。
    removed_last = fruits.pop()  # 移除並回傳最後一個元素。
    fruits.remove("grape")  # 移除第一個等於 grape 的元素。
    fruits[0] = "kiwi"  # list 可以修改元素。

    words = "Python is fun".split()  # str → list[str]
    sentence = " / ".join(words)  # list[str] → str

    position = (3, 5)
    x, y = position  # tuple 可以解包；元素本身不能重新指派。
    moved_position = (x + 1, y)  # 建立新的 tuple。

    player = {"name": "小貓", "score": 0}
    player["score"] += 1
    player["level"] = 2  # 新增 key，放在插入順序的最後面。

    skills = {"walk", "jump", "jump"}  # set 會去除重複元素。
    skills.add("run")
    skills.discard("swim")  # 沒有這個元素也不會拋出錯誤。
    other_skills = {"jump", "swim"}

    # 使用獨立的亂數產生器，不改變其他模組的全域亂數狀態。
    generator = random.Random(seed)
    return {
        "list": fruits,
        "list_length": len(fruits),
        "list_slice": fruits[1:3],
        "removed_last": removed_last,
        "has_banana": "banana" in fruits,
        "sorted_fruits": sorted(fruits),
        "words": words,
        "sentence": sentence,
        "position": position,
        "moved_position": moved_position,
        "player": player,
        "player_keys": list(player),
        "missing_key_default": player.get("lives", 3),
        "skills": sorted(skills),
        "union": sorted(skills | other_skills),
        "intersection": sorted(skills & other_skills),
        "difference": sorted(skills - other_skills),
        "frozen_skills": frozenset(skills),
        "dice": generator.randint(1, 6),
        "random_fruit": generator.choice(fruits),
        "sqrt_81": math.sqrt(81),
    }


def main() -> None:
    demo = build_demo()
    print("list 操作：", demo["list"])
    print("長度 / 切片：", demo["list_length"], demo["list_slice"])
    print("pop 的回傳值：", demo["removed_last"])
    print("banana 在串列裡：", demo["has_banana"])
    print("排序後的新串列：", demo["sorted_fruits"])
    print("split / join：", demo["words"], "→", demo["sentence"])
    print("tuple / 新 tuple：", demo["position"], "→", demo["moved_position"])
    print("dict：", demo["player"])
    print("dict 的插入順序：", demo["player_keys"])
    print("get 的預設值：", demo["missing_key_default"])
    # set 沒有保證順序；只在印出結果時排序，方便閱讀。
    print("set 去重：", demo["skills"])
    print("聯集 / 交集 / 差集：", demo["union"], demo["intersection"], demo["difference"])
    print("frozenset：", sorted(demo["frozen_skills"]))
    print("固定種子的亂數：骰子 =", demo["dice"], "；水果 =", demo["random_fruit"])
    print("import math：sqrt(81) =", demo["sqrt_81"])


if __name__ == "__main__":
    main()
