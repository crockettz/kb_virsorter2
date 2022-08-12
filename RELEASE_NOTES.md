# kb_virsorter2 release notes
=========================================

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
