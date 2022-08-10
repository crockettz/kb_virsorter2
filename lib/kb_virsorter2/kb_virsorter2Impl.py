# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import psutil

from installed_clients.KBaseReportClient import KBaseReport
from kb_virsorter2.kb_virmatcher_utils.virmatcher_utils import process_kbase_object, generate_report
from kb_virsorter2.kb_virmatcher_utils.virmatcher_runner import run_virsorter2
#END_HEADER


class kb_virsorter2:
    '''
    Module Name:
    kb_virsorter2

    Module Description:
    A KBase module: kb_virsorter2
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        self.ws_url = config['workspace-url']
        alt_cpu = psutil.cpu_count(logical=False)
        self.cpus = alt_cpu if alt_cpu < 32 else 32
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_kb_virsorter2(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kb_virsorter2
        logging.info('Getting input file parameters from KBase workspace for VirSorter2...')

        genomes_ref = params.get('genomes')
        if type(genomes_ref) != str:
            raise ValueError('input_object_ref is required and must be a string')

        logging.info('Processing input file')
        genomes_fp = process_kbase_object(
            genomes_ref, self.shared_folder, self.callback_url, self.ws_url, ctx['token']
        )

        ####
        logging.info('Passing input sequences to VirSorter2')
        virsorter2_dir = self.shared_folder / 'VirSorter2_results'
        run_virsorter2(genomes_fp, params, self.cpus, virsorter2_dir)






        logging.info('VirMatcher complete, sending results to KBase workspace')
        report_info = generate_report(self.callback_url, ctx['token'], params.get('workspace_name'),
                                      self.shared_folder, virsorter2_dir)





        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created':[],
                                                'text_message': params['parameter_1']},
                                                'workspace_name': params['workspace_name']})
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END run_kb_virsorter2

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_virsorter2 return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
