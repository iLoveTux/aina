#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `flume` package."""


import unittest
from click.testing import CliRunner

from flume.flume import cli


class TestFlume(unittest.TestCase):
    """Tests for `flume` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        help_result = runner.invoke(cli, ['--help'])
        self.assertEqual(help_result.exit_code, 0)
        self.assertIn('--help  Show this message and exit.', help_result.output)
