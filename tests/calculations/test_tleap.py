""" Tests for tleap calculations."""
import os

from aiida.engine import run
from aiida.plugins import CalculationFactory, DataFactory
from aiida_amber.data.tleap_input import TleapInputData
import subprocess
import sys


from .. import TEST_DIR


def run_tleap(amber_code):
    """Run an instance of sander and return the results."""

    # profile = load_profile()
    # computer = helpers.get_computer()
    # amber_code = helpers.get_code(entry_point="amber", computer=computer)

    # Prepare input parameters
    TleapParameters = DataFactory("amber.tleap")
    parameters = TleapParameters(
        {
            # "o": "01_Min.out",
            # "r": "01_Min.ncrst",
            # "inf": "01_Min.mdinfo",
        }
    )


    # set up calculation
    inputs = {
        "code": amber_code,
        "parameters": parameters,
        "metadata": {
            "description": "tleap test",
        },
    }

    # Prepare input parameters in AiiDA formats.
    # Set the tleap script as a TleapInputData type node
    inputs["tleapscript"] = TleapInputData(file=os.path.join(os.getcwd(), "tests/input_files/tleap", "tleap.in"))

    # Find the inputs and outputs referenced in the tleap script
    calc_inputs, calc_outputs = inputs["tleapscript"].calculation_inputs_outputs
    # add input files and dirs referenced in tleap file into inputs
    inputs.update(calc_inputs)
    inputs.update(calc_outputs)
    print("___", calc_inputs, calc_outputs)
    print("TEST_DIR", TEST_DIR)


    result = run(CalculationFactory("amber.tleap"), **inputs)
    # print("^^^", result)
    return result


def test_process(amber_code):
    """Test running a sander calculation.
    Note: this does not test that the expected outputs are created of output parsing"""

    result = run_tleap(amber_code)

    # assert "stdout" in result
    # assert "out" in result["tleap"]
    #assert "complex__prmtop" in result
    #assert "complex__inpcrd" in result


def test_file_name_match(amber_code):
    """Test that the file names returned match what was specified on inputs."""

    result = run_tleap(amber_code)

    # assert result["stdout"].list_object_names()[0] == "tleap.out"
    # assert result["tleap"]["out"].list_object_names()[0] == "tleap.out"
    #assert result["complex__prmtop"].list_object_names()[0] == "complex.prmtop"
    #assert result["complex__inpcrd"].list_object_names()[0] == "complex.inpcrd"