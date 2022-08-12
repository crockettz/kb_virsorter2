'''
Miscellaneous functions to handle kb_VirSorter2 that do not fall within running VirSorter2 proper
'''
import logging
from pathlib import Path
from Bio import SeqIO

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.WorkspaceClient import Workspace
from installed_clients.AssemblyUtilClient import AssemblyUtil


def process_kbase_object(genomes_ref, shared_folder, callback, workspace, token):
    """
    Convert KBase object(s) into usable files for VirSorter2
    :param genomes_ref: Viral genomes with KBase '#/#/#' used to describe each object
    :param shared_folder: KBase job node's "working" directory, where actual files exist
    :param callback:
    :param workspace: Workspace name
    :param token: Job token
    :return:
    """

    ws = Workspace(workspace, token=token)
    au = AssemblyUtil(callback, token=token)

    # Need to determine KBase type in order to know how to properly proceed
    genomes_type = ws.get_object_info3({'objects': [{'ref': genomes_ref}]})['infos'][0][2].split('-')[0]

    logging.info(f'Input type identified as: {genomes_type}')

    if genomes_type == 'KBaseGenomes.Genomes':  # TODO Get genomes working
        genome_data = ws.get_objects2({'objects': [
            {'ref': genomes_ref}]})['data'][0]['data']
        genome_data.get('contigset_ref') or genome_data.get('assembly_ref')

        genomes_fp = None

    elif genomes_type == 'KBaseGenomeAnnotations.Assembly':
        genomes_fp = au.get_assembly_as_fasta({'ref': genomes_ref})['path']

    else:
        raise ValueError(f'{genomes_type} is not supported.')

    records = SeqIO.parse(genomes_fp, 'fasta')
    virus_count = len(list(records))

    logging.info(f'{virus_count} sequences were identified.')

    return genomes_fp


def generate_report(callback_url, token, workspace_name, shared_folder: Path, virsorter2_output: Path):
    """
    :param callback_url:
    :param token: Job token
    :param workspace_name: Workspace name
    :param shared_folder: KBase working directory on the node, used to save the HTML file
    :param virsorter2_output: VirSorter2 proper final results directory, should have the summary file
    :return:
    """

    # Output folder containing information
    vs2_outdir = virsorter2_output
