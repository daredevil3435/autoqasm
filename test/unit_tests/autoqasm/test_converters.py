# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

"""Tests for the converters module."""

import pytest
from malt.core import ag_ctx, converter
from mock_transpiler import MockTranspiler

import autoqasm as aq
from autoqasm.converters import assignments


@pytest.fixture(autouse=True)
def program_ctx() -> None:
    return converter.ProgramContext(
        options=converter.ConversionOptions(recursive=True), autograph_module=aq.api
    )


def test_assignment(program_ctx: ag_ctx.ControlStatusCtx) -> None:
    """Tests the assignment converter.

    Args:
        program_ctx (ag_ctx.ControlStatusCtx): Transformer context.
    """

    def fn() -> None:
        """user program to test"""
        a = aq.IntVar(5)  # noqa: F841
        b = a  # noqa: F841
        c = 123  # noqa: F841
        d = (0.123, "foo")  # noqa: F841
        a = aq.IntVar(1)  # noqa: F841
        e = a  # noqa: F841
        f = aq.BoolVar(False)  # noqa: F841
        g = aq.BoolVar(True)  # noqa: F841
        g = f  # noqa: F841

    with aq.build_program() as program_conversion_context:
        mock_transpiler = MockTranspiler(assignments)
        transformed, _, _ = mock_transpiler.transform_function(fn, program_ctx)
        transformed()

    qasm = program_conversion_context.make_program().to_ir()
    expected_qasm = """OPENQASM 3.0;
int[32] b;
int[32] e;
int[32] a = 5;
b = a;
a = 1;
e = a;
bool f = false;
bool g = true;
g = f;"""
    assert qasm == expected_qasm


def test_break_for_loop():
    @aq.main
    def main():
        for i in aq.range(3):
            aq.gates.h(i)
            break

    with pytest.raises(aq.errors.UnsupportedFeatureError):
        main.build()


def test_break_while_loop():
    @aq.main
    def uses_while_w_break():
        while aq.gates.measure(0):
            aq.gates.x(0)
            break

    with pytest.raises(aq.errors.UnsupportedFeatureError):
        uses_while_w_break.build()
