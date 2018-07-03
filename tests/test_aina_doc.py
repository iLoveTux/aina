#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `aina stream` command."""
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
            with Path("src").open("w") as fp:
                fp.write("this is a {{test}}")
            with Path("namespace").open("w") as fp:
                fp.write("{'test': 'foo'}")
            runner.invoke(
                cli,
                args=(
                    "doc",
                    "--namespaces", "namespace",
                    "src",
                    "dst",
                )
            )
            with Path("dst").open("r") as fp:
                result = fp.read()
            expected = "this is a foo"
            self.assertEqual(expected, result)

    def test_simple_execution_and_substitution(self):
        """Test that simple execution and simple substitution
        works on a file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            with Path("src").open("w") as fp:
                fp.write("{% import re %}{{str(re.findall('\w+', 'this is a test'))}}")
            with Path("namespace").open("w") as fp:
                fp.write("{'test': 'foo'}")
            runner.invoke(
                cli,
                args=(
                    "doc",
                    "--namespaces", "namespace",
                    "src",
                    "dst",
                )
            )
            with Path("dst").open("r") as fp:
                result = fp.read()
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

            with Path(here / "src" / "first").open("w") as fp:
                fp.write("this is a {{test}}")
            with Path(here / "src" / "second").open("w") as fp:
                fp.write("this is another {{test}}")
            with Path(here / "namespace").open("w") as fp:
                fp.write("{'test': 'foo'}")

            runner.invoke(
                cli,
                args=(
                    "doc",
                    "--namespaces", "namespace",
                    "src",
                    "dst",
                )
            )
            with Path(here / "dst" / "first").open("r") as fp:
                first_result = fp.read()
            with Path(here / "dst" / "second").open("r") as fp:
                second_result = fp.read()
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

            with Path(here / "src" / "child"/ "nested").open("w") as fp:
                fp.write("this is a nested {{test}}")
            with Path(here / "src" / "first").open("w") as fp:
                fp.write("this is a {{test}}")
            with Path(here / "src" / "second").open("w") as fp:
                fp.write("this is another {{test}}")
            with Path(here / "namespace").open("w") as fp:
                fp.write("{'test': 'foo'}")

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
            # print(output.exception)
            with Path(here / "dst" / "first").open("r") as fp:
                first_result = fp.read()
            with Path(here / "dst" / "child" / "nested").open("r") as fp:
                nested_result = fp.read()
            with Path(here / "dst" / "second").open("r") as fp:
                second_result = fp.read()
            self.assertEqual("this is a foo", first_result)
            self.assertEqual("this is a nested foo", nested_result)
            self.assertEqual("this is another foo", second_result)