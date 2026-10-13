"""Check independent mutable state and method overriding in the class demo."""

import unittest

from examples.classes import Animal, Cat, Dog


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
