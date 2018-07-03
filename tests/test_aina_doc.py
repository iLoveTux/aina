#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `aina doc` command."""
import unittest
import logging
from pathlib import Path
from aina.aina import cli
from click.testing import CliRunner


class TestainaDoc(unittest.TestCase):
    """Tests for `aina doc` subcommand."""
    def test_simple_substitution(self):
        """Test that simple substitution works on a file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("src").write_text("this is a {{test}}")
            Path("namespace").write_text("{'test': 'foo'}")
            output = runner.invoke(
                cli,
                args=(
                    "doc",
                    "--namespaces", "namespace",
                    "src",
                    "dst",
                )
            )
            self.assertIs(output.exception, None)
            result = Path("dst").read_text()
            expected = "this is a foo"
            self.assertEqual(expected, result)

    def test_simple_execution_and_substitution(self):
        """Test that simple execution and simple substitution
        works on a file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("src").write_text("{% import re %}{{str(re.findall('\w+', 'this is a test'))}}")
            Path("namespace").write_text("{'test': 'foo'}")
            output = runner.invoke(
                cli,
                args=(
                    "doc",
                    "--namespaces", "namespace",
                    "src",
                    "dst",
                )
            )
            self.assertIs(output.exception, None)
            result = Path("dst").read_text()
            expected = "['this', 'is', 'a', 'test']"
            self.assertEqual(expected, result)

    def test_multiple_files(self):
        """Test that when a directory is given as src, all files
        will be rendered to dst"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            here = Path(".")
            Path(here / "dst").mkdir()
            Path(here / "src").mkdir()

            Path(here / "src" / "first").write_text("this is a {{test}}")
            Path(here / "src" / "second").write_text("this is another {{test}}")
            Path(here / "namespace").write_text("{'test': 'foo'}")

            output = runner.invoke(
                cli,
                args=(
                    "doc",
                    "--namespaces", "namespace",
                    "src",
                    "dst",
                )
            )
            print(output.output)
            self.assertIs(output.exception, None)
            first_result = Path(here / "dst" / "first").read_text()
            second_result = Path(here / "dst" / "second").read_text()

            self.assertEqual("this is a foo", first_result)
            self.assertEqual("this is another foo", second_result)

    def test_multiple_files_with_recursion(self):
        """Test that when a directory is given as src, and
        --recursive is passed all files will be rendered to dst
        recursively"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            here = Path(".")
            Path(here / "dst").mkdir()
            Path(here / "src").mkdir()
            Path(here / "src" / "child").mkdir()

            Path(here / "src" / "child"/ "nested").write_text("this is a nested {{test}}")
            Path(here / "src" / "first").write_text("this is a {{test}}")
            Path(here / "src" / "second").write_text("this is another {{test}}")
            Path(here / "namespace").write_text("{'test': 'foo'}")

            output = runner.invoke(
                cli,
                args=(
                    "doc",
                    "--namespaces", "namespace",
                    "--recursive",
                    "src",
                    "dst",
                )
            )
            self.assertIs(output.exception, None)
            first_result = Path(here / "dst" / "first").read_text()
            nested_result = Path(here / "dst" / "child" / "nested").read_text()
            second_result = Path(here / "dst" / "second").read_text()
            self.assertEqual("this is a foo", first_result)
            self.assertEqual("this is a nested foo", nested_result)
            self.assertEqual("this is another foo", second_result)

    def test_recursive_runs_top_down(self):
        """Test recursive visits files in a top-down manner"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            here = Path(".")
            Path(here / "dst").mkdir()
            Path(here / "src").mkdir()
            Path(here / "src" / "child").mkdir()

            # since we need to guarantee top-down recursion,
            # The alterations to the namespace from a top-most file
            # Should be available to the more nested files
            Path(here / "src" / "first").write_text("{%x='5'%}this is a {{test}}")
            Path(here / "src" / "second").write_text("this is another {{test}}")
            Path(here / "src" / "child"/ "nested").write_text("X: {{x}}")
            Path(here / "namespace").write_text("{'test': 'foo'}")

            output = runner.invoke(
                cli,
                args=(
                    "doc",
                    "--namespaces", "namespace",
                    "--recursive",
                    "src",
                    "dst",
                )
            )
            self.assertIs(output.exception, None)
            first_result = Path(here / "dst" / "first").read_text()
            nested_result = Path(here / "dst" / "child" / "nested").read_text()
            second_result = Path(here / "dst" / "second").read_text()
            self.assertEqual("this is a foo", first_result)
            self.assertEqual("X: 5", nested_result)
            self.assertEqual("this is another foo", second_result)

    def test_no_recursive_option_ignores_subdirectories(self):
        """Test child is not rendered without recursive flag"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            here = Path(".")
            Path(here / "dst").mkdir()
            Path(here / "src").mkdir()
            Path(here / "src" / "child").mkdir()

            # since we need to guarantee top-down recursion,
            # The alterations to the namespace from a top-most file
            # Should be available to the more nested files
            Path(here / "src" / "first").write_text("{%x='5'%}this is a {{test}}")
            Path(here / "src" / "second").write_text("this is another {{test}}")
            Path(here / "src" / "child"/ "nested").write_text("X: {{x}}")
            Path(here / "namespace").write_text("{'test': 'foo'}")

            output = runner.invoke(
                cli,
                args=(
                    "doc",
                    "--namespaces", "namespace",
                    "src",
                    "dst",
                )
            )
            self.assertIs(output.exception, None)
            first_result = Path(here / "dst" / "first").read_text()
            second_result = Path(here / "dst" / "second").read_text()
            self.assertFalse(Path(here / "dst" / "child").exists())
            self.assertEqual("this is a foo", first_result)
            self.assertEqual("this is another foo", second_result)

    def test_begins_are_executed_before_namespace_is_constructed(self):
        """Test that anything passed to --begins is executed
        before anything else."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("src").write_text("{{test}}")
            Path("namespace").write_text("{'test': str(sorted(os.listdir('.')))}")
            output = runner.invoke(
                cli,
                args=(
                    "doc",
                    "--begins", "import os",
                    "--namespaces", "namespace",
                    "src",
                    "dst",
                )
            )
            self.assertIs(output.exception, None)
            result = Path("dst").read_text()
            expected = "['namespace', 'src']"
            self.assertEqual(expected, result)


    def test_ends_are_executed_after_all_work_is_done(self):
        """Test that anything passed to --ends is executed
        after everything else."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("src").write_text("{% x = 5 %}{{test}}")
            Path("namespace").write_text("{'test': 'foo'}")
            output = runner.invoke(
                cli,
                args=(
                    "doc",
                    "--namespaces", "namespace",
                    "--ends", "print(locals())",
                    "src",
                    "dst",
                )
            )
            self.assertIs(output.exception, None)
            result = Path("dst").read_text()
            expected = "foo"
            self.assertEqual(expected, result)
            self.assertIn("'x': 5", output.output)
