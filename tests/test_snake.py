"""Rules that matter during play, tested without a display or Pygame."""

import random
import unittest

from games.snake import Direction, GameState, SnakeGame


class SnakeGameTests(unittest.TestCase):
    def test_eating_grows_once_and_scores_once(self) -> None:
        game = SnakeGame(rng=random.Random(7))
        game.fruit = (3, game.rows // 2)
        self.assertTrue(game.tick())
        self.assertEqual(game.score, 1)
        self.assertEqual(len(game.body), 4)
        self.assertNotIn(game.fruit, game.body)
        # A normal move still advances the head and keeps the new length.
        game.fruit = (0, 0)
        self.assertFalse(game.tick())
        self.assertEqual(game.head, (4, game.rows // 2))
        self.assertEqual((game.score, len(game.body)), (1, 4))

    def test_wall_collision_stops_round_without_corrupting_body(self) -> None:
        game = SnakeGame(4, 2)
        game.body = [(3, 0), (2, 0), (1, 0)]
        game.fruit = (0, 1)
        body_before = game.body.copy()
        self.assertFalse(game.tick())
        self.assertEqual(game.state, GameState.LOST)
        self.assertEqual(game.collision_at, (4, 0))
        self.assertEqual(game.body, body_before)
        self.assertFalse(game.tick())
        self.assertEqual(game.body, body_before)

    def test_self_collision_stops_round(self) -> None:
        game = SnakeGame(3, 3)
        game.body = [(1, 1), (1, 2), (0, 2), (0, 1), (0, 0), (1, 0)]
        game.direction = Direction.LEFT
        game.fruit = (2, 2)
        self.assertFalse(game.tick())
        self.assertEqual(game.state, GameState.LOST)
        self.assertEqual(game.collision_at, (0, 1))

    def test_moving_into_vacating_tail_is_legal(self) -> None:
        game = SnakeGame(3, 3)
        game.body = [(1, 1), (1, 2), (0, 2), (0, 1)]
        game.direction = Direction.LEFT
        game.fruit = (2, 2)
        self.assertFalse(game.tick())
        self.assertTrue(game.alive)
        self.assertEqual(game.body, [(0, 1), (1, 1), (1, 2), (0, 2)])

    def test_reversals_and_repeated_direction_are_rejected(self) -> None:
        game = SnakeGame()
        self.assertFalse(game.request_direction(Direction.LEFT))
        self.assertFalse(game.request_direction(Direction.RIGHT))
        self.assertTrue(game.request_direction(Direction.DOWN))
        # Reversing a queued turn would lead straight back into the body.
        self.assertFalse(game.request_direction(Direction.UP))
        game.tick()
        self.assertEqual(game.direction, Direction.DOWN)
        self.assertEqual(game.head, (2, game.rows // 2 + 1))

    def test_quick_corner_queues_two_turns_and_rejects_flooding(self) -> None:
        game = SnakeGame()
        self.assertTrue(game.request_direction("down"))
        self.assertTrue(game.request_direction("left"))
        self.assertFalse(game.request_direction("up"))
        self.assertFalse(game.request_direction("right"))
        game.tick()
        self.assertEqual(game.direction, Direction.DOWN)
        game.tick()
        self.assertEqual(game.direction, Direction.LEFT)
        self.assertEqual(game.head, (1, game.rows // 2 + 1))
        self.assertTrue(game.alive)

    def test_seeded_fruit_is_reproducible_and_never_on_body(self) -> None:
        first = SnakeGame(rng=random.Random(42))
        second = SnakeGame(rng=random.Random(42))
        for _ in range(50):
            first.spawn_fruit()
            second.spawn_fruit()
            self.assertEqual(first.fruit, second.fruit)
            self.assertNotIn(first.fruit, first.body)
            self.assertIsNotNone(first.fruit)
            x, y = first.fruit
            self.assertTrue(0 <= x < first.columns)
            self.assertTrue(0 <= y < first.rows)

    def test_fruit_uses_only_free_square_on_almost_full_board(self) -> None:
        game = SnakeGame(3, 3)
        game.body = [(x, y) for y in range(3) for x in range(3) if (x, y) != (2, 2)]
        game.spawn_fruit()
        self.assertEqual(game.fruit, (2, 2))
        self.assertTrue(game.alive)

    def test_last_fruit_wins_and_no_more_moves_are_accepted(self) -> None:
        game = SnakeGame(4, 1)
        self.assertEqual(game.fruit, (3, 0))
        self.assertTrue(game.tick())
        self.assertEqual(game.state, GameState.WON)
        self.assertEqual(game.score, 1)
        self.assertEqual(len(game.body), 4)
        self.assertIsNone(game.fruit)
        body_before = game.body.copy()
        self.assertFalse(game.tick())
        self.assertFalse(game.request_direction(Direction.DOWN))
        self.assertEqual(game.body, body_before)

    def test_already_full_board_wins_without_recursing(self) -> None:
        game = SnakeGame(1, 1)
        self.assertEqual(game.state, GameState.WON)
        self.assertIsNone(game.fruit)

    def test_reset_clears_score_and_queued_turns_and_isolates_instances(self) -> None:
        game = SnakeGame(rng=random.Random(3))
        other = SnakeGame(rng=random.Random(3))
        game.fruit = (3, game.rows // 2)
        game.tick()
        game.request_direction(Direction.DOWN)
        game.reset()
        self.assertEqual(game.score, 0)
        self.assertEqual(game.state, GameState.RUNNING)
        self.assertIsNone(game.collision_at)
        self.assertEqual(game.body, other.body)
        self.assertIsNot(game.body, other.body)
        game.fruit = (0, 0)
        game.tick()
        self.assertEqual(game.direction, Direction.RIGHT)
        self.assertEqual(other.head, (2, other.rows // 2))
        self.assertEqual(len(other.body), 3)

    def test_invalid_dimensions_or_length_fail_early(self) -> None:
        for arguments in ({"columns": 0}, {"rows": -1}, {"initial_length": 0}):
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    SnakeGame(**arguments)


if __name__ == "__main__":
    unittest.main()
