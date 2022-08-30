import logging
from pathlib import Path
import subprocess


def run_virsorter2(genome_fp: Path, args, cpu_count, output_dir: Path):
    """

    Note - does not require decoy virus info because it is now embedded in package
    :param genome_fp:
    :param args:
    :param cpu_count:
    :param output_dir:
    :return:
    """

    # TODO Not included --seqname-suffix-off

    # Need to "build up" command
    virsorter_cmd = ['virsorter', 'run', '-w', str(output_dir), '-i', str(genome_fp), '-j', str(cpu_count)]

    bool_args = ['enable_dramv', 'exclude_short', 'require_all_hallmarks', 'keep_original',
                 'require_short_hallmarks', 'highconfidence_only', 'disable_provirus',
                 'viral_gene_required', 'viral_gene_enrichment']  # Checkboxes
    bool_params = ['--prep-for-dramv', '--exclude-lt2gene', '--hallmark-required', '--keep-original-seq',
                   '--hallmark-required-on-short', '--high-confidence-only', '--provirus-off',
                   '--viral-gene-required', '--viral-gene-enrich-off']

    for bool_arg, bool_param in zip(bool_args, bool_params):
        print(f'{bool_arg}, {bool_param}')
        try:
            print('---', args[bool_arg])
            if args[bool_arg] == '1':
                print(f'{bool_arg} flag enabled.')
                virsorter_cmd.extend([bool_param])
        except KeyError:  # arg not present (i.e. KBase user doesn't provide)
            print(f'{bool_arg} not provided, using default.')

    # Numerical
    numerical_args = ['minimum_score', 'minimum_length', 'max_orfs']
    numerical_params = ['--min-score', '--min-length', '--max-orf-per-seq']

    for numerical_arg, numerical_param in zip(numerical_args, numerical_params):
        virsorter_cmd.extend([numerical_param, str(args[numerical_arg])])

    # List of ,-joined elements
    included_groups = ','.join(args['included_groups'])
    virsorter_cmd.extend(['--include-groups', included_groups])

    # Closing
    virsorter_cmd.extend(['--use-conda-off', 'all'])

    logging.info(f'Running VirSorter2 command:\n{" ".join([str(cmd) for cmd in virsorter_cmd])}')

    ret = subprocess.run(virsorter_cmd, check=True)

    if ret.returncode != 0:
        logging.error(f'There was an issue during VirMatcher execution: {ret.stderr}')
        exit(1)
