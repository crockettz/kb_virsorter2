# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser

from kb_virsorter2.kb_virsorter2Impl import kb_virsorter2
from kb_virsorter2.kb_virsorter2Server import MethodContext
from kb_virsorter2.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace


class kb_virsorter2Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_virsorter2'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_virsorter2',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = kb_virsorter2(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_your_method(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods

        # Local tests
        raw_assembly_ref = "31160/20/1"  # KBaseGenomeAnnotations.Assembly-3.0 --> verified working
        genome_ref = "31160/82/1"  # KBaseGenomes.Genome-11.0 / VirSorter-Category-2_Genome --> verified working
        bins_ref = "31160/72/1"  # KBaseMetagenomes.BinnedContigs-1.0 / VirSorter_binnedContigs --> verified working
        assembly_set_ref = "31160/80/1"  # KBaseSets.AssemblySet‑1.2 / VirSorter-cat1256-AssemblySet --> verified works
        contigset_ref = ""  # TODO KBaseGenomes.ContigSet

        ret = self.serviceImpl.run_kb_virsorter2(
            self.ctx,
            {
                'workspace_name': self.wsName,
                'genomes': assembly_set_ref,
                'enable_dramv': '1',  # Default = 0
                'exclude_short': '0',  #
                'viral_gene_required': '0',
                'viral_gene_enrichment': '0',
                'require_all_hallmarks': '0',
                'max_orfs': '-1',  # Default = -1 here, but repo is not
                'keep_original': '0',  # Trim sequence
                'require_short_hallmarks': '0',  # Don't require
                'minimum_length': '0',  # No min length
                'highconfidence_only': '0',
                'minimum_score': '0.5',
                'included_groups': ['dsDNAphage', 'ssDNA'],
                'disable_provirus': '0'
            })
