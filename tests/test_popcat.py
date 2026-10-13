"""Input regression tests that run without a display or Pygame installed."""

import unittest

from games.popcat import PopcatState


class PopcatInputTests(unittest.TestCase):
    def test_held_input_does_not_count_key_repeat(self) -> None:
        state = PopcatState()

        self.assertTrue(state.press("key:space"))
        for _ in range(20):
            self.assertFalse(state.press("key:space"))

        self.assertEqual(state.clicks, 1)
        self.assertTrue(state.mouth_open)

    def test_release_then_press_counts_a_new_pop(self) -> None:
        state = PopcatState()
        state.press("mouse")
        state.release("mouse")

        self.assertFalse(state.mouth_open)
        self.assertEqual(state.clicks, 1)
        self.assertTrue(state.press("mouse"))
        self.assertEqual(state.clicks, 2)
        self.assertTrue(state.mouth_open)

    def test_mouse_and_keyboard_overlap_keep_mouth_open(self) -> None:
        for first_to_release in ("mouse", "key:space"):
            with self.subTest(first_to_release=first_to_release):
                state = PopcatState()
                state.press("mouse")
                state.press("key:space")
                self.assertEqual(state.clicks, 2)

                state.release(first_to_release)
                self.assertTrue(state.mouth_open)
                other = "key:space" if first_to_release == "mouse" else "mouse"
                state.release(other)
                self.assertFalse(state.mouth_open)
                self.assertEqual(state.clicks, 2)

    def test_unknown_release_leaves_active_input_held(self) -> None:
        state = PopcatState()
        state.press("mouse")
        state.release("key:enter")

        self.assertTrue(state.mouth_open)
        self.assertFalse(state.press("mouse"))
        self.assertEqual(state.clicks, 1)

    def test_focus_loss_closes_mouth_and_preserves_score(self) -> None:
        state = PopcatState()
        state.press("mouse")
        state.press("key:space")
        state.release_all()

        self.assertFalse(state.mouth_open)
        self.assertEqual(state.clicks, 2)
        self.assertTrue(state.press("mouse"))
        self.assertEqual(state.clicks, 3)

    def test_reset_clears_score_and_held_input(self) -> None:
        state = PopcatState()
        state.press("mouse")
        state.press("key:enter")
        state.reset()

        self.assertEqual(state.clicks, 0)
        self.assertFalse(state.mouth_open)
        self.assertTrue(state.press("mouse"))
        self.assertEqual(state.clicks, 1)

    def test_two_cats_have_independent_scores_and_held_inputs(self) -> None:
        first = PopcatState()
        second = PopcatState()
        first.press("mouse")

        self.assertFalse(second.mouth_open)
        self.assertEqual(second.clicks, 0)
        self.assertTrue(second.press("mouse"))
        first.reset()

        self.assertFalse(first.mouth_open)
        self.assertEqual(first.clicks, 0)
        self.assertTrue(second.mouth_open)
        self.assertEqual(second.clicks, 1)


if __name__ == "__main__":
    unittest.main()
