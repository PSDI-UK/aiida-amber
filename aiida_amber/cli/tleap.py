#!/usr/bin/env python
"""Command line utility to run amber tleap command with AiiDA.

Usage: aiida_tleap --help
"""

import os
import sys
import click

from aiida import cmdline, engine
from aiida.plugins import CalculationFactory, DataFactory

from aiida_amber import helpers
from aiida_amber.data.tleap_input import TleapInputData

# from aiida_amber.utils import searchprevious


def launch(params):
    """Run tleap.

    Uses helpers to add amber on localhost to AiiDA on the fly.

    - get inputs and outputs
    - check if they are files
    - add them as nodes
    """

    # Prune unused CLI parameters from dict.
    params = {k: v for k, v in params.items() if v is not None}
    # print(params)

    #print(params)
    #print(os.path.join(os.getcwd(), params["f"]))
    # test1 = TleapInputData(file=os.path.join(os.getcwd(), params["f"]))
    # print(test1.attributes)
    # sys.exit()

    # dict to hold our calculation data.
    inputs = {
        "metadata": {
            "description": params.pop("description"),
        },
    }

    # If code is not initialised, then setup.
    if "code" in inputs:
        inputs["code"] = params.pop("code")
    else:
        computer = helpers.get_computer()
        inputs["code"] = helpers.get_code(entry_point="tleap", computer=computer)

    # Prepare input parameters in AiiDA formats.
    SinglefileData = DataFactory("core.singlefile")
    # inputs["tleapfile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("f")))
    inputs["tleapfile"] = TleapInputData(file=os.path.join(os.getcwd(), params.pop("f")))
    calc_inputs, calc_outputs = inputs["tleapfile"].calculation_inputs
    # add input files and dirs referenced in tleap file into inputs
    inputs.update(calc_inputs)
    inputs.update(calc_outputs)
    # print(inputs, inputs["tleapfile"].outfile_list)
    print(inputs)


    if "i" in params:
        for i, subdir in enumerate(params["i"]):
            inputs["dirs"][f"dir{i}"] = SinglefileData(
                file=os.path.join(os.getcwd(), subdir)
            )
        params.pop("i")

    TleapParameters = DataFactory("amber.tleap")
    inputs["parameters"] = TleapParameters(params)

    # check if inputs are outputs from prev processes
    # inputs = searchprevious.get_prev_inputs(inputs, ["tprfile"])

    # check if a pytest test is running, if so run rather than submit aiida job
    # Note: in order to submit your calculation to the aiida daemon, do:
    # pylint: disable=unused-variable
    if "PYTEST_CURRENT_TEST" in os.environ:
        future = engine.run(CalculationFactory("amber.tleap"), **inputs)
    else:
        future = engine.submit(CalculationFactory("amber.tleap"), **inputs)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
# Plugin options
@click.option(
    "--description",
    default="record tleap data provenance via the aiida_amber plugin",
    type=str,
    help="Short metadata description",
)
# Input file options
@click.option(
    "-f", default="tleapfile", type=str, help="input file for tleap commands"
)
@click.option(
    "-I",
    type=str, multiple=True,
    help="dir containing leaprc files",
)
def cli(*args, **kwargs):
    # pylint: disable=unused-argument
    # pylint: disable=line-too-long
    """Run example.

    Example usage:

    $ aiida_tleap --code tleap@localhost -f input_files/tleap.in

    Alternative (automatically tried to create amber@localhost code, but requires
    amber to be installed and available in your environment path):

    $ aiida_tleap -f input_files/tleap.in

    Help: $ aiida_tleap --help
    """

    launch(kwargs)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
