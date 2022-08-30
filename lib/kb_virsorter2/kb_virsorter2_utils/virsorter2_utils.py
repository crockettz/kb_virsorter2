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
from installed_clients.MetagenomeUtilsClient import MetagenomeUtils

html_template = Template("""<!DOCTYPE html>
<html lang="en">
<head>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/5.1.3/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.datatables.net/1.12.1/css/jquery.dataTables.min.css" rel="stylesheet">
  <link href="https://cdn.datatables.net/buttons/2.2.3/css/buttons.dataTables.min.css" rel="stylesheet">
  <link href="https://cdn.datatables.net/searchpanes/2.0.2/css/searchPanes.dataTables.min.css" rel="stylesheet">
  <link href="https://cdn.datatables.net/select/1.4.0/css/select.dataTables.min.css" rel="stylesheet">

  <script src="https://code.jquery.com/jquery-3.5.1.js" type="text/javascript"></script>
  <script src="https://cdn.datatables.net/1.12.1/js/jquery.dataTables.min.js" type="text/javascript"></script>
  <script src="https://cdn.datatables.net/1.12.1/js/dataTables.bootstrap5.min.js" type="text/javascript"></script>
  <script src="https://cdn.datatables.net/buttons/2.2.3/js/dataTables.buttons.min.js" type="text/javascript"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js" type="text/javascript"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/pdfmake.min.js" type="text/javascript"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/vfs_fonts.js" type="text/javascript"></script>
  <script src="https://cdn.datatables.net/buttons/2.2.3/js/buttons.html5.min.js" type="text/javascript"></script>
  <script src="https://cdn.datatables.net/buttons/2.2.3/js/buttons.print.min.js" type="text/javascript"></script>
  <script src="https://cdn.datatables.net/searchpanes/2.0.2/js/dataTables.searchPanes.min.js" type="text/javascript"></script>
  <script src="https://cdn.datatables.net/select/1.4.0/js/dataTables.select.min.js" type="text/javascript"></script>

  <style>
  tfoot input {
    width: 100%;
    padding: 3px;
    box-sizing: border-box;
  }
  </style>

</head>

<body>
  <div class="container">
    <div>
      ${html_table}
    </div>  
  </div>

  <script type="text/javascript">
    $$(document).ready(function () {
      // Setup - add a text input to each footer cell
      $$('#my_dataframe tfoot th').each(function () {
        var title = $$(this).text();
        $$(this).html('<input type="text" placeholder="Search ' + title + '" />');
      });

      // DataTable
      var table = $$('#my_dataframe').DataTable({
        dom: 'lPBfrtip',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ],
        initComplete: function () {
          // Apply the search
          this.api()
          .columns()
          .every(function () {
            var that = this;

            $$('input', this.footer()).on('keyup change clear', function () {
              if (that.search() !== this.value) {
                that.search(this.value).draw();
              }
            });
          });
        },
      });

      // Add buttons
      // new $$.fn.dataTable.Buttons( table, {
      //   buttons: [
      //     'copy', 'excel', 'pdf', 'csv', 'print'
      //   ]
      // } );
    });
  </script>

</body>
</html>""")


def process_kbase_object(genomes_ref, shared_folder: Path, callback, workspace, token):
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
    dfu = DataFileUtil(callback, token=token)
    mgu = MetagenomeUtils(callback, token=token)

    # Need to determine KBase type in order to know how to properly proceed
    genomes_type = ws.get_object_info3({'objects': [{'ref': genomes_ref}]})['infos'][0][2].split('-')[0]

    logging.info(f'Input type identified as: {genomes_type}')

    # TODO "KBaseMetagenomes.Genomes"
    # TODO "KBaseSets.GenomeSet" OR "KBaseSearch.GenomeSet"

    if genomes_type in ['KBaseGenomes.Genome', 'KBaseGenomeAnnotations.Assembly', 'KBaseGenomes.ContigSet']:

        if genomes_type == 'KBaseGenomes.Genome':  # Does KBaseGenomes.Genomes exist?

            data = ws.get_objects2(
                {'objects': [
                    {'ref': genomes_ref,
                     'included': ['assembly_ref'],
                     'strict_maps': 1}]
                })['data'][0]['data']

            genome_ref = data['assembly_ref']

            records_ref = genome_ref

        elif genomes_type in ['KBaseGenomeAnnotations.Assembly', 'KBaseGenomes.ContigSet']:
            records_ref = genomes_ref

        else:
            raise ValueError(f'{genomes_type} is not supported.')

        records_fp = au.get_assembly_as_fasta({'ref': records_ref})['path']

        if not Path(records_fp).is_file():
            raise ValueError('Error generating fasta file from an Assembly or ContigSet with AssemblyUtil')

        records = SeqIO.parse(records_fp, 'fasta')
        virus_count = len(list(records))

    # For "sets" (including BinnedContigs), want to *merge* sequence files
    elif genomes_type == 'KBaseSets.AssemblySet':
        assemblyset_data = dfu.get_objects({'object_refs': [genomes_ref]})['data'][0]

        assemblyset_records = []
        for assemblySet in assemblyset_data['data']['items']:
            assembly_fp = au.get_assembly_as_fasta({'ref': assemblySet['ref']})['path']

            suffix = Path(assembly_fp).suffix
            if suffix in ['.fasta', '.fna', '.fa']:  # Must be fasta to be consumed

                assemblyset_record = SeqIO.parse(assembly_fp, 'fasta')
                assemblyset_records.extend(assemblyset_record)

            else:
                raise ValueError(f'{suffix} is not supported as a KBaseSets.AssemblySet object.')

        records_fp = shared_folder / 'KBaseSets.AssemblySet.fasta'
        SeqIO.write(assemblyset_records, records_fp, 'fasta')

        virus_count = len(assemblyset_records)

    elif genomes_type == 'KBaseMetagenomes.BinnedContigs':

        binned_contig_dir = mgu.binned_contigs_to_file(
            {
                'input_ref': genomes_ref,
                'save_to_shock': 0
            }
        )['bin_file_directory']  # Dict of bin_file_dir and shock_id

        binnedcontg_records = []
        for (dirpath, dirnames, fns) in os.walk(binned_contig_dir):  # Dirnames = all folders under dirpath
            for fn in fns:

                binnedcontig_fp = Path(dirpath) / fn

                binnedcontg_record = SeqIO.parse(binnedcontig_fp, 'fasta')
                binnedcontg_records.extend(binnedcontg_record)

        records_fp = shared_folder / 'KBaseMetagenomes.BinnedContigs.fasta'
        SeqIO.write(binnedcontg_records, records_fp, 'fasta')

        virus_count = len(binnedcontg_records)

    else:
        raise ValueError(f'{genomes_type} is not supported.')

    logging.info(f'{virus_count} sequences were identified.')

    return records_fp


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
    au = AssemblyUtil(callback_url)

    # Need to archive VC2 output results - save the 3 output files so users can download
    boundary_fp = virsorter2_output / 'final-viral-boundary.tsv'
    fasta_fp = virsorter2_output / 'final-viral-combined.fa'
    scores_fp = virsorter2_output / 'final-viral-score.tsv'

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
            'path': str(tar_fp),
            'name': tar_fp.name,
            'label': tar_fp.name,
            'description': desc
        })

    # Save KBase FASTA file as assembly object
    assembly_fp = output_dir / fasta_fp.name
    shutil.copy(fasta_fp, assembly_fp)

    created_objects = []
    assembly_obj = au.save_assembly_from_fasta(
        {
            'file': {
                'path': str(assembly_fp)
            },
            'assembly_name': 'VirSorter2-Assembly',
            'workspace_name': workspace_name
        }
    )
    created_objects.append({
        "ref": assembly_obj,
        "description": "KBase.Assembly object from VirSorter2"
    })

    # In the case for DRAM-v compatability, save DRAM-v input
    # Check if affi-contigs exist. *could* check for presence of --prep-for-dramv flag in params, or just file presence
    affi_contigs_fp = virsorter2_output / 'for-dramv/viral-affi-contigs-for-dramv.tab'
    print('VirSorter2Output')
    print(os.listdir(virsorter2_output))
    print(os.listdir(virsorter2_output / 'for-dramv'))
    if affi_contigs_fp.exists():
        print('exists')
        affi_contigs_shock_fp = output_dir / 'affi-contigs.tab'
        shutil.copy(affi_contigs_fp, affi_contigs_shock_fp)

        affi_contigs_shock_id = dfu.file_to_shock({
            'file_path': str(affi_contigs_shock_fp)
        })['shock_id']
    else:
        affi_contigs_shock_id = False

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
                                ' to the KBase assembly object.\n',
                     'workspace_name': workspace_name,
                     'html_links': html_report,  # +1 HTML file in output_dir
                     'file_links': export_fps,  # 3 results files in output_dir
                     'direct_html_link_index': 0,
                     'report_object_name': f'VirSorter2_report_{str(uuid.uuid4())}',
                     'objects_created': created_objects  # KBase assembly
                     }  # Also shock_id for affi-contigs in output_dir

    if affi_contigs_shock_id:
        report_params['message'] += f'For users who enabled DRAM-v compatibility, the ' \
                                    f'shock ID is {affi_contigs_shock_id}'

    report_output = report.create_extended_report(report_params)

    return report_output
