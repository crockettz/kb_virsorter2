# kb_virsorter2 release notes
=========================================

0.1.1
------
* Allow users to change assembly object name

0.1.0
------
* Official beta release
* Added a check to ensure correctly formatted FASTA files
* Removed superfluous output
* Additional local KBase object test

0.0.16
------
* Almost finished flags...

0.0.15
------
* Almost finished flags...

0.0.14
------
* Further investigating of enabled flags

0.0.13
------
* Investigate affi contigs filenaming for DRAM-v

0.0.12
------
* Fix affi contigs filenaming for DRAM-v

0.0.11
------
* Added KBaseMetagenomes.BinnedContigs as input type
* Added KBaseSets.AssemblySet as input type
* Added KBaseGenomes.ContigSet as input type
* Fixed potential Pathlib-subprocess error
* NOTE: All "grouped" objects are reduced to flat FASTA files, dropping any grouping information (other than what might be stored in deflines)

0.0.10
------
* Fix --include-groups error

0.0.9
-----
* Fix subprocess arg error

0.0.8
-----
* Fix f-string error
* Fix potential error related to --included-groups in spec.json

0.0.7
-----
* Fix KeyError from users not providing optional arguments

0.0.6
-----
* Address VS2 DB setup issue

0.0.5
-----
* Updated binnedContig to assembly
* Fixed "boolean" in runner code
* Major overhaul/update to HTML report - +DataTables+SearchPanes+Buttons
* Adjusted DRAM-v compatibility code
* Fixed Pathing issues
* Added --viral-gene-required and --viral-gene-enrich-off
* Fixed output --> KBase report issue(s)
* Updated server test with additional parameters

0.0.4
-----
* Add saving VS2 results as downloads (boundary, scores, genome fasta)
* Build assembly object
* Add shock_id for DRAM-v compatibility
* Build HTML report

0.0.3
-----
* Added AssemblyUtil and DateFileUtil clients
* Fixed VS2 Dockerfile dependencies
* Fixed inconsistencies between specs
* Update Entrypoint for VS2 DB issue
* Fix VS2 run command
* WARNING: Module will run and VS2 will do so successfully, but KBase report isn't "connected", so overall will fail.

0.0.2
-----
* Added VirSorter2 runner for underlying tool
* Added utility function to interact with KBase objects
* Added server test
* Added loose logic to kb_virsorter2Impl.py, though report not functional

0.0.1
-----
* Added spec.json content
* Added kb_virsorter2.spec content
* Added display.yaml content
* Added Dockerfile
* Added database information to entrypoint

0.0.0
-----
* Module created by kb-sdk init
