#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `aina stream` command."""
import unittest
import logging
from aina.aina import cli
from click.testing import CliRunner


class TestainaStream(unittest.TestCase):
    """Tests for `aina stream` subcommand."""

    def setUp(self):
        """Set up test fixtures, if any."""
        # Need this to overcome an issue with testing
        # basically clearing configuration from the last
        # call to invoke because, i think, that between
        # calls sys.stdout is replaced but logging configuration
        # persists through runs leaving a stale reference to
        # the old sys.stdout
        logging.getLogger("").handlers = []


    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_simple_substitution(self):
        """Test that simple substitution works."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            args=(
                "stream",
                "--templates",
                "{{line}}"
            ),
            input="foo"
        )
        expected = "foo\n"
        self.assertEqual(expected, result.output)

    def test_begin_lines_only_executed_when_tests_pass(self):
        """Test `--begin-lines` is only executed when all tests pass."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            args=(
                "stream",
                "--tests", "'bar' in line",
                "--begin-lines", "print(line, end='')"
            ),
            input="foo\nbar\n"
        )
        expected = "bar\n"
        self.assertEqual(expected, result.output)

    def test_end_lines_only_executed_when_tests_pass(self):
        """Test `--end-lines` is only executed regardless of the results of test."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            args=(
                "stream",
                "--tests", "'bar' in line.strip()",
                "--end-lines", "print(line.strip())",
            ),
            input="foo\nbar\n"
        )
        expected = "foo\nbar\n"
        self.assertEqual(expected, result.output)

    def test_only_renders_if_test_pass(self):
        """Test that templates only render if test passes."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            args=(
                "stream",
                "--tests", "'bar' in line",
                "--templates", "{{line}}"
            ),
            input="foo\nbar"
        )
        expected = "bar\n"
        self.assertEqual(expected, result.output)

    def test_only_renders_if_all_tests_pass(self):
        """Test that templates only render if all tests passes."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            args=(
                "stream",
                "--tests", "'bar' in line",
                "--tests", "'foo' in line",
                "--templates", "{{line}}",
            ),
            input="foo\nbar\nfoobar",
        )
        expected = "foobar\n"
        self.assertEqual(expected, result.output)

    def test_help_menu(self):
        """Test the CLI."""
        runner = CliRunner()
        help_result = runner.invoke(cli, ['stream', '--help'])
        self.assertEqual(help_result.exit_code, 0)
        self.assertIn('Show this message and exit.', help_result.output)
