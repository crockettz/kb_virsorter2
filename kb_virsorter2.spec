/*
A KBase module: kb_virsorter2
*/

module kb_virsorter2 {

    typedef string obj_ref;

    typedef structure {
        string report_name;
        string report_ref;
        obj_ref genomes;
        string enable_dramv;
        string exclude_short;
        string require_all_hallmarks;
        string max_orfs;
        string keep_original;
        string require_short_hallmarks;
        string minimum_length;
        string highconfidence_only;
        string minimum_score;
        string included_groups;
        string disable_provirus;

    } InParams;

    typedef structure{
        string report_name
        string report_ref
        string result_directory;
        obj_ref binned_contig_obj_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_kb_virsorter2(InParams params)
        returns (ReportResults report_output) authentication required;

};
