"""Check teaching examples at their boundaries and common beginner pitfalls."""

import math
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from examples import basics
from examples.basics import (
    factorial,
    factorial_recursive,
    fibonacci,
    fibonacci_recursive,
)
from examples.classes import Animal, Cat, Dog
from examples.containers import build_demo


class NumberExamplesTests(unittest.TestCase):
    def test_launcher_can_supply_its_own_arguments(self):
        output = StringIO()
        with patch("sys.argv", ["main.py", "--example", "basics"]):
            with redirect_stdout(output):
                basics.main([])
        self.assertIn("6! = 720", output.getvalue())

    def test_factorial_zero_and_known_value(self):
        self.assertEqual(factorial(0), 1)
        self.assertEqual(factorial(6), math.factorial(6))
        self.assertEqual(factorial_recursive(0), 1)
        self.assertEqual(factorial_recursive(6), factorial(6))

    def test_fibonacci_starts_at_zero(self):
        expected = [0, 1, 1, 2, 3, 5, 8, 13]
        self.assertEqual([fibonacci(n) for n in range(8)], expected)
        self.assertEqual([fibonacci_recursive(n) for n in range(8)], expected)

    def test_numbers_reject_negative_and_non_integer_input(self):
        for operation in (factorial, fibonacci, factorial_recursive, fibonacci_recursive):
            with self.subTest(operation=operation.__name__, value=-1):
                with self.assertRaises(ValueError):
                    operation(-1)
            for value in (True, False, "5", 1.5, None):
                with self.subTest(operation=operation.__name__, value=value):
                    with self.assertRaises(TypeError):
                        operation(value)

    def test_recursive_demo_limits(self):
        self.assertEqual(factorial_recursive(100), math.factorial(100))
        self.assertEqual(fibonacci_recursive(20), 6765)
        with self.assertRaises(ValueError):
            factorial_recursive(101)
        with self.assertRaises(ValueError):
            fibonacci_recursive(21)
        # The iterative versions remain usable outside the teaching limits.
        self.assertEqual(factorial(101), math.factorial(101))
        self.assertEqual(fibonacci(21), 10946)


class ContainerExamplesTests(unittest.TestCase):
    def test_seed_reproduces_random_demo(self):
        self.assertEqual(build_demo(seed=7), build_demo(seed=7))
        demo = build_demo(seed=7)
        self.assertIn(demo["dice"], range(1, 7))
        self.assertIn(demo["random_fruit"], demo["list"])

    def test_container_results_and_insertion_order(self):
        demo = build_demo()
        self.assertEqual(demo["player_keys"], ["name", "score", "level"])
        self.assertEqual(demo["intersection"], ["jump"])
        self.assertIsInstance(demo["frozen_skills"], frozenset)
        # A caller changing one result must not change the next invocation.
        demo["list"].append("new fruit")
        self.assertNotIn("new fruit", build_demo()["list"])


class ClassExamplesTests(unittest.TestCase):
    def test_each_instance_has_its_own_tricks(self):
        first, second = Dog("first"), Dog("second")
        first.add_trick("sit")
        self.assertEqual(first.tricks, ["sit"])
        self.assertEqual(second.tricks, [])
        self.assertIsNot(first.tricks, second.tricks)

    def test_inheritance_and_method_overriding(self):
        animals = [Animal("animal"), Dog("dog"), Cat("cat")]
        self.assertTrue(all(isinstance(animal, Animal) for animal in animals))
        self.assertEqual([animal.talk() for animal in animals], ["...", "woof", "meow"])
        self.assertEqual(animals[2].describe(), "cat (cat)：meow")

    def test_empty_names_and_tricks_are_rejected(self):
        with self.assertRaises(ValueError):
            Dog(" ")
        with self.assertRaises(TypeError):
            Cat(None)
        dog = Dog("dog")
        with self.assertRaises(ValueError):
            dog.add_trick("")
        with self.assertRaises(TypeError):
            dog.add_trick(1)


if __name__ == "__main__":
    unittest.main()
