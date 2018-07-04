#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `aina` package."""


import unittest
from aina.render import render

class TestainaRender(unittest.TestCase):
    """Tests for `aina` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.namespace = {
            "x": 42,
            "y": "foo",
            "z": True
        }

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_simple_substitution(self):
        """Test simple substitution."""
        input = "{{'5'}}"
        expected = "5"
        self.assertEqual(render(input), expected)

    def test_namespace_simple_substitution(self):
        input = "{{y}}"
        expected = "foo"
        self.assertEqual(render(input, self.namespace), expected)

    def test_namespace_substitution_with_function_call(self):
        input = "{{str(x)}}"
        expected = "42"
        self.assertEqual(render(input, self.namespace), expected)

    def test_simple_exec(self):
        input = "{% x = 5 %}{{str(x)}}"
        expected = "5"
        self.assertEqual(render(input, self.namespace), expected)
        self.assertEqual(self.namespace["x"], 5)

    def test_simple_exec_import(self):
        input = "{% import string %}{{string.ascii_letters}}"
        expected_in = "abcdefghijklmnopqrstuvwxyz"
        self.assertIn(expected_in, render(input, self.namespace))

    def test_multiline_template(self):
        input = """{%
                def foo():
                    return "bar"

                bar = foo()
            %}{{bar}}"""
        expected = "bar"
        self.assertEqual(render(input, self.namespace), expected)

    def test_multiline_substitution(self):
        input = """{{
            str(["foo", "bar", "baz"])
        }}"""
        expected = "['foo', 'bar', 'baz']"
        self.assertEqual(render(input, self.namespace), expected)

    def test_expression_replaced_with_stdout(self):
        input = "{%print('hello, world')%}"
        expected = "hello, world\n"
        self.assertEqual(render(input, self.namespace), expected)
