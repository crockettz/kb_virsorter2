/*
A KBase module: kb_virsorter2
*/

module kb_virsorter2 {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_kb_virsorter2(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
