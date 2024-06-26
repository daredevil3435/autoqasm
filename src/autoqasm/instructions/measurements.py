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

"""Quantum measurement on qubits.

Example of measuring qubit 0:

.. code-block:: python

    @aq.main
    def my_program():
        measure(0)
"""

from __future__ import annotations

from collections.abc import Iterable

from autoqasm import program
from autoqasm import types as aq_types
from autoqasm.instructions.qubits import GlobalQubitRegister, _qubit, global_qubit_register


def measure(
    qubits: aq_types.QubitIdentifierType | Iterable[aq_types.QubitIdentifierType] | None = None,
) -> aq_types.BitVar:
    """Add qubit measurement statements to the program and assign the measurement
    results to bit variables.

    Args:
        qubits (QubitIdentifierType | Iterable[QubitIdentifierType] | None): The target qubits
            to measure. If None, all qubits will be measured. Default is None.

    Returns:
        BitVar: Bit variable the measurement results are assigned to.
    """
    if qubits is None:
        qubits = global_qubit_register()

    if aq_types.is_qubit_identifier_type(qubits) and not isinstance(qubits, GlobalQubitRegister):
        qubits = [qubits]

    oqpy_program = program.get_program_conversion_context().get_oqpy_program()

    bit_var_size = len(qubits) if len(qubits) > 1 else None
    bit_var = aq_types.BitVar(
        size=bit_var_size,
        needs_declaration=True,
    )
    oqpy_program.declare(bit_var)

    qubits = [_qubit(qubit) for qubit in qubits]
    if len(qubits) == 1:
        oqpy_program.measure(qubits[0], bit_var)
    else:
        for idx, qubit in enumerate(qubits):
            oqpy_program.measure(qubit, bit_var[idx])

    return bit_var
