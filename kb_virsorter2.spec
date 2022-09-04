/*
A KBase module: kb_virsorter2
*/

module kb_virsorter2 {

    typedef string obj_ref;

    typedef structure {
        string workspace_name;
        string workspace_id;
        string report_name;
        string report_ref;
        obj_ref genomes;
        string assembly_object_name;
        string minimum_score;
        string minimum_length;
        string keep_original;
        string exclude_short;
        string enable_dramv;
        string highconfidence_only;
        string require_all_hallmarks;
        string require_short_hallmarks;
        string max_orfs;
        string viral_gene_required;
        string viral_gene_enrichment;
        string disable_provirus;
        string included_groups;

    } InParams;

    typedef structure{
        string report_name;
        string report_ref;
        string result_directory;
        obj_ref assembly_obj_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_kb_virsorter2(InParams params)
        returns (ReportResults report_output) authentication required;

};
