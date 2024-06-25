#!/usr/bin/env python
"""Command line utility to run amber pdb4amber command with AiiDA.

Usage: aiida_pdb4amber --help
"""

import os

import click

from aiida import cmdline, engine
from aiida.orm import SinglefileData
from aiida.plugins import CalculationFactory, DataFactory

from aiida_amber import helpers

# from aiida_amber.utils import searchprevious


def launch(params):
    """Run pdb4amber.

    Uses helpers to add amber on localhost to AiiDA on the fly.
    """

    # Prune unused CLI parameters from dict.
    params = {k: v for k, v in params.items() if v is not None}

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
        inputs["code"] = helpers.get_code(entry_point="pdb4amber", computer=computer)

    # Prepare input parameters in AiiDA formats.
    inputs["input_file"] = SinglefileData(
        file=os.path.join(os.getcwd(), params.pop("i"))
    )

    Pdb4amberParameters = DataFactory("amber.pdb4amber")
    inputs["parameters"] = Pdb4amberParameters(params)

    # need to search previous processes properly
    # check if inputs are outputs from prev processes
    # inputs = searchprevious.append_prev_nodes(inputs, inputs["input_list"])

    # check if a pytest test is running, if so run rather than submit aiida job
    # Note: in order to submit your calculation to the aiida daemon, do:
    # pylint: disable=unused-variable
    if "PYTEST_CURRENT_TEST" in os.environ:
        future = engine.run(CalculationFactory("amber.pdb4amber"), **inputs)
    else:
        future = engine.submit(CalculationFactory("amber.pdb4amber"), **inputs)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
# Plugin options
@click.option(
    "--description",
    default="record pdb4amber data provenance via the aiida_amber plugin",
    type=str,
    help="Short metadata description",
)

# Required inputs
@click.option("-i", default="stdin", type=str, help="PDB input file (default: stdin)")  # file
# Required outputs
@click.option("-o", default="stdout", type=str, help="PDB output file (default: stdout)")  # file

# optional output files
@click.option(
    "--logfile", "-l",
    type=int,
    help="FILE log filename",
)
@click.option(
    "--leap-template",
    type=str,
    help="write a leap template for easy adaption (EXPERIMENTAL)",
)

# other parameters
@click.option(
    "--nohyd", "-y",
    type=str,
    help="remove all hydrogen atoms (default: no)",
)
@click.option(
    "--dry", "-d",
    type=str,
    help="remove all water molecules (default: no)",
)
@click.option(
    "--strip", "-s",
    type=str,
    help="""STRIP_ATOM_MASK
            Strip given atom mask, (default: no)""",
)
@click.option(
    "--mutate", "-m",
    type=str,
    help="""MUTATION_STRING
            Mutate residue""",
)
@click.option(
    "--prot", "-p",
    type=str,
    help="keep only protein residues (default: no)",
)
@click.option(
    "-rn",
    type=str,
    help="residue name, overrides input file, default is MOL",
)
@click.option(
    "--amber-compatible-residues", "-a",
    type=str,
    help="keep only Amber-compatible residues (default: no)",
)
@click.option(
    "--constantph",
    type=str,
    help="rename GLU,ASP,HIS for constant pH simulation",
)
@click.option(
    "--most-populous",
    type=str,
    help="keep most populous alt. conf. (default is to keep 'A')",
)
@click.option(
    "--keep-altlocs",
    type=str,
    help="Keep alternative conformations",
)
@click.option(
    "--reduce",
    type=str,
    help="Run Reduce first to add hydrogens. (default: no)",
)
@click.option(
    "--no-reduce-db",
    type=str,
    help="""If reduce is on, skip using it for hetatoms. 
            (default: usual reduce behavior for hetatoms)""",
)
@click.option(
    "--pdbid",
    type=str,
    help="""fetch structure with given pdbid, should combined with -i option. 
            Subjected to change""",
)
@click.option(
    "--add-missing-atoms",
    type=str,
    help="Use tleap to add missing atoms. (EXPERIMENTAL OPTION)",
)
@click.option(
    "--model",
    type=str,
    help="""MODEL
            Model to use from a multi-model pdb file (integer). 
            (default: use 1st model). 
            Use a negative number to keep all models""",
)
@click.option(
    "--version", "-v",
    type=str,
    help="version",
)
@click.option(
    "--no-conect",
    type=str,
    help="do Not write S-S CONECT records",
)
@click.option(
    "--noter",
    type=str,
    help="do Not write TER records",
)
def cli(*args, **kwargs):
    # pylint: disable=unused-argument
    # pylint: disable=line-too-long
    """Run example.

    Example usage:

    $ aiida_pdb4amber --code pdb4amber@localhost -i protein.pdb

    Alternative (automatically tried to create amber@localhost code, but requires
    amber to be installed and available in your environment path):

    $ aiida_pdb4amber -i protein.pdb

    Help: $ aiida_pdb4amber --help
    """

    launch(kwargs)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
