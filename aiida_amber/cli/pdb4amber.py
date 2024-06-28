#!/usr/bin/env python
"""Command line utility to run amber pdb4amber command with AiiDA.

Usage: aiida_pdb4amber --help
"""

import os
import sys
import click

from aiida import cmdline, engine, orm
from aiida.orm import SinglefileData
from aiida.plugins import CalculationFactory, DataFactory

from aiida_amber import helpers

# from aiida_amber.utils import searchprevious


def launch(params):
    """Run pdb4amber.

    Uses helpers to add amber on localhost to AiiDA on the fly.

    Possible output files:

    if -o stdout and -l log.txt:

    stdout_renum.txt
    stdout_nonprot.pdb
    stdout_water.pdb
    stdout_sslink
    leap.template.in
    log.txt

    if -o test.pdb:
    test.pdb
    test_nonprot.pdb
    test_renum.txt
    test_sslink
    test_water.pdb
    
    """

    # Prune unused CLI parameters from dict.
    params = {k: v for k, v in params.items() if v not in [None, False]}

    print(params)
    print()
    print(params["o"])
    # sys.exit()

    # dict to hold our calculation data.
    inputs = {
        "metadata": {
            "description": params.pop("description"),
            # "options": {
            #     "output_filename": params["o"]} # need to set name of stdout 
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
        file=os.path.join(os.getcwd(), params.pop("in"))
    )

    # get all possible output files from arguments provided
    # pdb4amber appends the prefix of filename defined in -o flag to some
    # outputted files
    prefix = params["o"].split(".")[0]
    output_filenames = [f"{prefix}_sslink", f"{prefix}_nonprot.pdb", f"{prefix}_renum.txt"]
    if "dry" in params:
        water_file = f"{prefix}_water.pdb"
        output_filenames.append(water_file)
    if "leap-template" in params:
        output_filenames.append("leap.template.in")
    if "logfile" in params:
        output_filenames.append(params.pop("log_file"))
    inputs["pdb4amber_outfiles"] = orm.List(output_filenames)

    Pdb4amberParameters = DataFactory("amber.pdb4amber")
    inputs["parameters"] = Pdb4amberParameters(params)

    print(inputs["parameters"].cmdline_params)
    # sys.exit()

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
@click.option("-i", "--in", 
        default="input.pdb", 
        type=str, 
        help="PDB input file (default: input.pdb)")  # file in
# Required outputs
@click.option("-o", 
        default="stdout", 
        type=str, 
        help="PDB output file (default: stdout)")  # file out

# optional output files
@click.option(
     "-l", "--logfile",
    type=str,
    help="FILE log filename", # file out
)
@click.option(
    "--leap-template",
    is_flag=True,
    help="write a leap template for easy adaption (EXPERIMENTAL)", #file out
)

# other parameters
@click.option(
    "-y", "--nohyd", 
    is_flag=True,
    help="remove all hydrogen atoms (default: no)",
)
@click.option(
     "-d", "--dry",
    is_flag=True,
    help="remove all water molecules (default: no)", # file out
)
@click.option(
    "-s", "--strip", 
    type=str,
    help="""STRIP_ATOM_MASK
            Strip given atom mask, (default: no)""",
)
@click.option(
    "-m", "--mutate", 
    type=str,
    help="""MUTATION_STRING
            Mutate residue""",
)
@click.option(
    "-p", "--prot", 
    is_flag=True,
    help="keep only protein residues (default: no)",
)
@click.option(
    "-rn",
    type=str,
    help="residue name, overrides input file, default is MOL",
)
@click.option(
    "-a", "--amber-compatible-residues", 
    type=str,
    help="keep only Amber-compatible residues (default: no)",
)
@click.option(
    "--constantph",
    is_flag=True,
    help="rename GLU,ASP,HIS for constant pH simulation",
)
@click.option(
    "--most-populous",
    is_flag=True,
    help="keep most populous alt. conf. (default is to keep 'A')",
)
@click.option(
    "--keep-altlocs",
    is_flag=True,
    help="Keep alternative conformations",
)
@click.option(
    "--reduce",
    is_flag=True,
    help="Run Reduce first to add hydrogens. (default: no)",
)
@click.option(
    "--no-reduce-db",
    is_flag=True,
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
    is_flag=True,
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
    "-v", "--version", 
    is_flag=True,
    help="version",
)
@click.option(
    "--no-conect",
    is_flag=True,
    help="do Not write S-S CONECT records",
)
@click.option(
    "--noter",
    is_flag=True,
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
