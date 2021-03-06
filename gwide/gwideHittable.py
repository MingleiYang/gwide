#!/usr/bin/env python
import os, argparse
from argparse import RawTextHelpFormatter
import gwide.methods as gtm
import gwide.Classes.HittableClass as ghc

def hittable():
    ## option parser
    usage = "For more options type -h"
    description = "Downstream analysis on hittables crated by pyReadCounter. Chose type of analysys Usage: create hittables using pyReadCounter then run script in the folder containing hittables"
    parser = argparse.ArgumentParser(usage=usage, description=description)
    #functions
    parser.add_argument('--output', required=True, dest="function", choices=['correlation', 'count', 'piechart', 'classes'], help='REQUIRED, Calculate "correlations"; '
                                                                                                                         '"count" hittables for further analysis. Ideal to work with multiple experiments; '
                                                                                                                         'Plot "piechart"s for hittable classes')
    # parser for input files options
    files = parser.add_argument_group('Input file options')
    files.add_argument("-g", dest="gtf_file", help="Provide the path to your gtf file.", type=str, default=None)
    files.add_argument("--stdin", dest="stdin", action="store_true", help="Use standard input instead ./*hittable* Default: False", default=False)
    # universal options
    universal = parser.add_argument_group('universal options')
    universal.add_argument("-n", dest="normalized", action="store_true", help="Use when you want to work on data normalized 'reads per Milion'. Default: False", default=False)
    universal.add_argument("-w", dest="whole_name", action="store_true", help="As defauls scripts takes 'a_b_c' from a_b_c_hittable_reads.txt as experiment name. Use this option if your file names do not suit to this pattern. Default: False", default=False)
    universal.add_argument("-p", dest="out_prefix", type=str, help="Prefix for output files.", default=None)
    # parser specific for counts
    corr_group = parser.add_argument_group("counts options")
    corr_group.add_argument("--rpkm", dest="rpkm", action="store_true", help="Use RPKM instead of hits. Default: False", default=False)
    # parser specific for correlations
    corr_group = parser.add_argument_group("correlation options")
    corr_group.add_argument("-c", dest="gene_class", action="store_true", help="Calculate Pearson coefficient for different classes separately. Default: False", default=False)
    corr_group.add_argument("-o", dest="output", choices=["p", "s", "k", "a"], help="Select from following options: p - Pearson (standard correlation coefficient); s - Spearman rank correlation; k - Kendall Tau correlation coefficient; a - all at once", default="p")
    #parser specific for piecharts
    piechart_group = parser.add_argument_group("piechart options")
    piechart_group.add_argument("-s", "--single", dest="print_single", help="Print hittables in single files",
                             action="store_true", default=False)
    options = parser.parse_args()

    ## Creating HittableClass object
    data = ghc.HittableClass(gtf=gtm.getGTF(options.gtf_file), whole_name=options.whole_name, n_rpM=options.normalized, out_prefix=options.out_prefix, read_stdin=options.stdin)

    #running chosen function
    if options.function == 'correlation':
        data.correlation(output=options.output, gene_class=options.gene_class)
    elif options.function == 'count':
        data.count(normalize=options.normalized, use_RPKM=options.rpkm)
    elif options.function == 'piechart':
        data.plot(print_single=options.print_single)
    elif options.function == 'classes':
        data.classes_to_tab()
    print "Done."