#!/usr/bin/env python
"""Command line utility to run amber cpptraj command with AiiDA.

Usage: aiida_cpptraj --help
"""

import os

import click

from aiida import cmdline, engine
from aiida.orm import SinglefileData
from aiida.plugins import CalculationFactory, DataFactory

from aiida_amber import helpers
from aiida_amber.data.cpptraj_input import CpptrajInputData
from aiida_amber.utils import node_utils

# from aiida_amber.utils import searchprevious


def launch(params):
    """Run cpptraj.

    Uses helpers to add amber on localhost to AiiDA on the fly.
    """

    # Prune unused CLI parameters from dict.
    params = {k: v for k, v in params.items() if v not in [None, False]}

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
        inputs["code"] = helpers.get_code(entry_point="cpptraj", computer=computer)

    # Prepare input parameters in AiiDA formats.
    # Set the tleap script as a TleapInputData type node
    inputs["cpptraj_script"] = CpptrajInputData(
        file=os.path.join(os.getcwd(), params.pop("input"))
    )

    # Find the inputs and outputs referenced in the tleap script
    calc_inputs, calc_outputs = inputs["cpptraj_script"].calculation_inputs_outputs
    # add input files and dirs referenced in tleap file into inputs
    inputs.update(calc_inputs)
    inputs.update(calc_outputs)

    if "parm" in params:
        inputs["prmtop_files"] = {}
        parm_list = list(params["parm"].split())
        # params.pop("parm")
        for parmfile in parm_list:
            formatted_filename = node_utils.format_link_label(parmfile)
            # inputs["prmtop_files"] = List(parm_list)
            inputs["prmtop_files"][formatted_filename] = SinglefileData(
                file=os.path.join(os.getcwd(), parmfile)
            )
    if "inpcrd" in params:
        inputs["inpcrd_files"] = {}
        inpcrd_list = list(params["inpcrd"].split())
        # params.pop("inpcrd")
        # inputs["inpcrd_files"] = List(inpcrd_list)
        for inpcrdfile in inpcrd_list:
            formatted_filename = node_utils.format_link_label(inpcrdfile)
            inputs["inpcrd_files"][formatted_filename] = SinglefileData(
                file=os.path.join(os.getcwd(), inpcrdfile)
            )

    # correct the flags that should contain a dash "-"
    # rather than an underscore "_"
    if "no_splash" in params:
        del params["no_splash"]
        params["no-splash"] = True
    if "enable_interpreter" in params:
        del params["enable_interpreter"]
        params["enable-interpreter"] = True

    CpptrajParameters = DataFactory("amber.cpptraj")
    inputs["parameters"] = CpptrajParameters(params)

    # need to search previous processes properly
    # check if inputs are outputs from prev processes
    # inputs = searchprevious.append_prev_nodes(inputs, inputs["input_list"])

    # check if a pytest test is running, if so run rather than submit aiida job
    # Note: in order to submit your calculation to the aiida daemon, do:
    # pylint: disable=unused-variable
    if "PYTEST_CURRENT_TEST" in os.environ:
        future = engine.run(CalculationFactory("amber.cpptraj"), **inputs)
    else:
        future = engine.submit(CalculationFactory("amber.cpptraj"), **inputs)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
# Plugin argument
@click.argument(
    "file",
    nargs=-1,
    required=False,
    # help="* A topology, input trajectory, or file containing cpptraj input."
)
# Plugin options
@click.option(
    "--description",
    default="record cpptraj data provenance via the aiida_amber plugin",
    type=str,
    help="Short metadata description",
)

# Required inputs
@click.option(
    "-i",
    default="cpptraj.inp",
    type=str,
    help="* Read input from <Input0>.",
)  # file in

# optional input files
@click.option(
    "-p",
    multiple=True,
    type=str,
    help="* Load <Top0> as a topology file.",
)  # file in
@click.option(
    "-y",
    multiple=True,
    type=str,
    help="""* Read from trajectory file <trajin>;
            same as input ’trajin <trajin>’.""",
)  # file in
@click.option(
    "-c",
    multiple=True,
    type=str,
    help="""* Read <reference> as reference coordinates;
            same as input 'reference <reference>'.""",
)  # file in
@click.option(
    "-d",
    multiple=True,
    type=str,
    help="""* Read data in from file <datain> ('readdata <datain>').""",
)  # file in

# Required outputs


# optional output files
@click.option(
    "-x",
    multiple=True,
    type=str,
    help="""* Write trajectory file <trajout>;
            same as input ’trajout <trajout>’.""",
)  # file out
@click.option(
    "-w",
    type=str,
    help="""Write data from <datain> as file <dataout> ('writedata <dataout>).""",
)  # file out
@click.option(
    "-o",
    type=str,
    help="""Write CPPTRAJ STDOUT output to file <output>.""",
)  # file out
@click.option(
    "--log",
    type=str,
    help="""Record commands to <logfile> (interactive mode only).
            Default is 'cpptraj.log'.""",
)  # file out

# other parameters
@click.option("-ya", multiple=True, type=str, help="* Input trajectory file arguments.")
@click.option(
    "-xa", multiple=True, type=str, help="* Output trajectory file arguments."
)
@click.option(
    "-V",
    "--version",
    is_flag=True,
    help="""Print version and exit.""",
)
@click.option(
    "--defines",
    is_flag=True,
    help="""Print compiler defines and exit.""",
)
@click.option(
    "-debug",
    type=str,
    help="""Set global debug level to <#>; same as input 'debug <#>'.""",
)
@click.option(
    "--interactive",
    is_flag=True,
    help="""Force interactive mode.""",
)
@click.option(
    "-tl",
    is_flag=True,
    help="""Print length of all input trajectories specified on
            the command line to STDOUT.""",
)
@click.option(
    "-ms",
    type=str,
    help="""Print selected atom numbers to STDOUT.""",
)
@click.option(
    "-mr",
    type=str,
    help="""Print selected residue numbers to STDOUT.""",
)
@click.option(
    "-mask",
    type=str,
    help="""Print detailed atom selection to STDOUT.""",
)
@click.option(
    "--resmask",
    type=str,
    help="""Print detailed residue selection to STDOUT.""",
)
@click.option(
    "--rng",
    type=str,
    help="""Change default random number generator.""",
)
def cli(*args, **kwargs):
    # pylint: disable=unused-argument
    # pylint: disable=line-too-long
    """Run example.

    Example usage:

    $ aiida_cpptraj --code cpptraj@localhost -i cpptraj.inp

    Alternative (automatically tried to create amber@localhost code, but requires
    amber to be installed and available in your environment path):

    $ aiida_cpptraj -i cpptraj.inp

    Help: $ aiida_cpptraj --help

    * Denotes flag may be specified multiple times.
    """

    launch(kwargs)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
