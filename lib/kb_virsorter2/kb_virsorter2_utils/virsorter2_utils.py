'''
Miscellaneous functions to handle kb_VirSorter2 that do not fall within running VirSorter2 proper
'''
import logging
import shutil
from string import Template
from pathlib import Path
from Bio import SeqIO
import uuid
import os
import tarfile
import pandas as pd

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.WorkspaceClient import Workspace
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.DataFileUtilClient import DataFileUtil

html_template = Template("""<!DOCTYPE html>
<html lang="en">
  <head>
    <link href="https://cdn.datatables.net/1.12.1/css/jquery.dataTables.min.css" rel="stylesheet">

    <script src="https://code.jquery.com/jquery-3.5.1.js" type="text/javascript"></script>
    <script src="https://cdn.datatables.net/1.12.1/js/jquery.dataTables.min.js" type="text/javascript"></script>

  </head>

  <body>
    <div class="container">
      <div>
        ${html_table}
      </div>  
    </div>

    <script type="text/javascript">
      $$(document).ready(function () {
        $$('#my_dataframe').DataTable();
      });
    </script>

  </body>
</html>""")


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

    Save the 3 results files for external use (e.g. download)
    Save the predicted virus FASTA file as assembly object
    Save shock_id of DRAM-v file
    "Export" scores into HTML report, allowing users to visual results

    :param callback_url:
    :param token: Job token
    :param workspace_name: Workspace name
    :param shared_folder: KBase working directory on the node, used to save the HTML file
    :param virsorter2_output: VirSorter2 proper final results directory, should have the summary file
    :return:
    """

    report = KBaseReport(callback_url, token=token)
    dfu = DataFileUtil(callback_url, token=token)

    # Need to archive VC2 output results - save the 3 output files so users can download
    boundary_fp = virsorter2_output / 'final-viral-boundary.tsv'
    fasta_fp = virsorter2_output / 'final-viral-combined.fa'
    scores_fp = virsorter2_output / 'final-viral-scores.tsv'

    # Output directory to store HTML and final results files
    output_dir = shared_folder / str(uuid.uuid4())
    os.mkdir(output_dir)

    # Want to send all these to KBase
    export_fps = []

    # Compress each of them to save KBase disk space
    boundary_tgz = output_dir / f'{boundary_fp.name}.tar.gz'
    fasta_tgz = output_dir / f'{fasta_fp.name}.tar.gz'
    scores_tgz = output_dir / f'{scores_fp.name}.tar.gz'

    # Need to give descriptions for each file
    boundary_desc = 'Table with boundary information'
    fasta_desc = 'Viral sequences in FASTA format'
    scores_desc = 'Table with scoring information'

    for tar_fp, fp, desc in zip([boundary_tgz, fasta_tgz, scores_tgz],
                                [boundary_fp, fasta_fp, scores_fp],
                                [boundary_desc, fasta_desc, scores_desc]):

        with tarfile.open(tar_fp, 'w:gz') as tar_fh:
            tar_fh.add(fp, arcname=fp.name)

        export_fps.append({
            'path': tar_fp,
            'name': tar_fp.name,
            'label': tar_fp.name,
            'description': desc
        })

    # Save KBase FASTA file as assembly object
    assembly_fp = output_dir / fasta_fp.name
    shutil.copy(fasta_fp, assembly_fp)

    created_objects = []
    assembly_obj = AssemblyUtil.save_assembly_from_fasta({
        'file': {
            'path': str(assembly_fp)
        },
        'workspace_name': workspace_name,
        'assembly_name': 'VirSorter2-Assembly'
    })
    created_objects.append({
        "ref": assembly_obj,
        "description": "KBase.Assembly object from VirSorter2"
    })

    # In the case for DRAM-v compatability, save DRAM-v input
    affi_contigs_fp = virsorter2_output / 'affi-contigs.tab'
    affi_contigs_shock_fp = output_dir / 'affi-contigs.tab'
    shutil.copy(affi_contigs_fp, affi_contigs_shock_fp)

    affi_contigs_shock_id = dfu.file_to_shock({
        'file_path': affi_contigs_shock_fp
    })['shock_id']

    # Create HTML report that incorporates and displays the virus scores to allow users to go through results
    scores_df = pd.read_csv(scores_fp, header=0, index_col=None, delimiter='\t')

    scores_html = scores_df.to_html(header=True, index=False, classes='my_class striped" id = "my_dataframe')

    footer = "<tfoot>\n" + " ".join(["<th>" + i + "</th>\n" for i in scores_df.columns]) + "</tr>\n  </tfoot>"

    scores_html = scores_html.replace("</table>", footer + "</table>")

    html = html_template.substitute(html_table=scores_html)

    # Save report (i.e. HTML) to shock
    html_fp = output_dir / 'index.html'

    with open(html_fp, 'w') as html_fh:
        html_fh.write(html)

    report_shock_id = dfu.file_to_shock({
        'file_path': str(output_dir),
        'pack': 'zip'
    })['shock_id']

    html_report = [{
        'shock_id': report_shock_id,
        'name': 'index.html',
        'label': 'index.html',
        'description': 'Summary report for VirSorter2'
    }]

    report_params = {'message': 'Results from your VirSorter2 run. Above you\'ll find a report with the identified,'
                                '*putative* virus genomes, and below, downloadable links to the results files and links'
                                ' to the KBase assembly object.\n. For users who enabled DRAM-v compatibility, the '
                                f'shock ID is {affi_contigs_shock_id}',
                     'workspace_name': workspace_name,
                     'html_links': html_report,  # +1 HTML file in output_dir
                     'file_links': export_fps,  # 3 results files in output_dir
                     'direct_html_link_index': 0,
                     'report_object_name': f'VirSorter2_report_{str(uuid.uuid4())}',
                     'objects_created': created_objects  # KBase assembly
                     }  # Also shock_id for affi-contigs in output_dir

    report_output = report.create_extended_report(report_params)

    return report_output
