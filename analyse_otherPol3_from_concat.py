#!/usr/bin/env python
__author__ = 'Tomasz Turowski'
__copyright__	= "Copyright 2015"
__version__		= "0.2"
__credits__		= ["Tomasz Turowski"]
__email__		= "twturowski@gmail.com"
__status__		= "Production"

from optparse import OptionParser
import select
import os

from gwide.gwideToolkit.otherPol3FromConcat import *


""" Script working with concat file generated by pileupsToConcat.py script. Can work on stdin from that script. Read concat file and according to options.
Can plot intron, and peaks found by pypeaks script.
Possibilities:
plot per page - one experiment, different genes
              - one gene, different experiments
              - one 3` end of RNA in nucleotide resolution
              - and many others
Slightly modified version of analyse_tRNA_from_concat.py
              """

def main():
    usage = "Usage: create pileups with pyPileup (pyCRAC package) then in directory containing pileup files type run i.e.:"+"\n"+ \
            "analyse_otherPol3_from_concat.py -c file.concat"
    parser = OptionParser(usage=usage)
    parser.add_option("-g", "--gtf_file", dest="gtf_file", help="Provide the path to your gtf file.",
                     metavar="FILE", default=os.environ['GTF_PATH'])
    parser.add_option("-c", "--concat_file", dest="concat_file", help="Provide the path to your concat file.",
                     metavar="FILE", default=None)
    parser.add_option("--abox", dest="abox_file", help="Provide the path to your tab file with A box start.",
                     metavar="FILE", default=None)
    parser.add_option("--bbox", dest="bbox_file", help="Provide the path to your tab file with B box start.",
                     metavar="FILE", default=None)
    parser.add_option("--5flank", dest="five_prime_flank", type="int", help="Set up 5 prime flank in pileup file. Default = 250", default=250)
    parser.add_option("--3flank", dest="three_prime_flank", type="int", help="Set up 3 prime flank in pileup file. Default = 250", default=250)
    parser.add_option("-l", "--lookahead", dest="lookahead", type="int", help="Set up lookahead parameter for pypeaks function. Default = 20", default=20)
    parser.add_option("-t", "--hits_threshold", dest="hits_threshold", type="int", help="Set up threshold for pileup. Default 100 reads",
                      default=100)
    parser.add_option("-r", "--readthrough", dest="readthrough", type="int", help="Set up when readthrough should start countin. Default: 0",
                      default=0)
    parser.add_option("-w", "--window", dest="window", type="int", help="Set up size of window for energy calculation. Default: 5",
                      default=5)
    parser.add_option("-a", dest="to_divide", type="str", help="experiment to divide by -b",
                      default=None)
    parser.add_option("-b", dest="divisor", type="str", help="experiment being divisor for -a",
                      default=None)
    parser.add_option("-p", "--prefix", dest="out_prefix", type="str", help="Prefix for output files. Default to standard output. Not supported for -o ratio.", default=None)
    parser.add_option("--peaks", dest="print_peaks", action="store_true", help="Add into command line if you want to print peaks on plots. Default: False",
                      default=False)
    parser.add_option("--valleys", dest="print_valleys", action="store_true", help="Add into command line if you want to print valleys on plots. Works only with -o figstd. Default: False",
                      default=False)
    parser.add_option("-o", "--output", dest="output_files", choices=["text", "fig", "both", "nuc", "nuc_gene", "figstd", "boxes", "energy", "ratio", "termination_valleys", "termination", "termination_text"], help="Select from following options:"+'\n'
                                                                                                   "text - only text, tab-deliminated;"+'\n'
                                                                                                   "figstd - only plots, gene after gene "+'\n'
                                                                                                   "boxes - only plots, gene after gene, including A and B boxes "+'\n'
                                                                                                   "energy - plots with nucleotide ressolution and energy plots" + '\n'
                                                                                                   "fig - only plots, gene sorted; nuc - for nucleotide 3` end resolution"+'\n'
                                                                                                   "nuc_gene - for nucleotide resolution of gene only"+'\n'
                                                                                                   "termination_valleys - for each valley calculate termination efficiency"+'\n'
                                                                                                   "termination - calculate termination efficiency for last 20 nt"+'\n'
                                                                                                   "termination_text - calculate termination efficiency for last 20 nt and print text file"+'\n'
                                                                                                   "both - plots and text file; ratio - log2 for -a divided by -b", default="both")
    parser.add_option("-n", "--normalized", dest="normalized", action="store_true", help="Use when you want to work on data normalized reads per Milion? Default: False", default=False)
    (options, args) = parser.parse_args()

    if not select.select([sys.stdin,],[],[],0.0)[0] and not options.concat_file: #expression from stackoverflow to check if there are data in standard input
        print usage
        print 'For more details use -h option.'
        exit()
    if options.concat_file:
        concat_file = open(options.concat_file)
    else:
        concat_file = sys.stdin

    gtf_file = options.gtf_file

    if options.output_files == 'boxes' and ( options.abox_file == None or options.bbox_file == None ):
        print 'Please provide path to both box.tab files using options --abox and --bbox.'
        exit()

    if options.out_prefix:
        prefix = options.out_prefix+'_'
        filename = options.out_prefix+'_rt'+str(options.readthrough)+'_l'+str(options.lookahead)+'_t'+str(options.hits_threshold)+'.list'
    else:
        prefix = str()
        text_file = sys.stdout
        filename = 'rt'+str(options.readthrough)+'_l'+str(options.lookahead)+'_t'+str(options.hits_threshold)+'.list'

    if options.print_peaks == True:
        prefix = prefix+'peaks_'
    if options.print_valleys == True:
        prefix = prefix+'valleys_'

    if options.output_files == "ratio":
        options.normalized = True

    if options.output_files == 'termination_valleys':
        options.print_peaks = True
        options.print_valleys = True

    data = OtherPol3FromConcat(gtf_file=gtf_file, five_prime_flank=options.five_prime_flank, print_valleys=options.print_valleys, print_peaks=options.print_peaks, readthrough_start=options.readthrough,
                             three_prime_flank=options.three_prime_flank, hits_threshold=options.hits_threshold, lookahead=options.lookahead, prefix=prefix, normalized=options.normalized)
    if options.output_files != "ratio":
        data.read_concat_file(concat_file, null_substitution=False)
    elif options.output_files == "ratio":
        data.read_concat_file(concat_file, null_substitution=True) ## makes all 0 as 1 in hittable

    if (options.print_peaks == True or options.print_valleys == True) and options.output_files != "ratio":
        data.find_peaks()

    data.calculate_read_through()
    if options.output_files == "text" or options.output_files == "both":
        text_file = open(filename, "w")
        data.make_text_file(text_file)
  #      data.test_print()

    if options.output_files == "fig" or options.output_files == "both":
        data.create_features_to_plot()
        # data.slice_dataframe()
        data.fig_gene_pp()

    if options.output_files == "ratio":
        data.slice_dataframe()
        data.fig_ratio(options.to_divide, options.divisor)

    if options.output_files == "nuc":
        data.fig_nucleotide_resolution()

    if options.output_files == "nuc_gene":
        data.create_features_to_plot()
        data.fig_nucleotide_gene()

    if options.output_files == "energy":
        data.fig_energy(options.window)

    if options.output_files == "figstd":
        data.create_features_to_plot()
        # data.slice_dataframe()
        data.fig_gene_after_gene()

    if options.output_files == "boxes":
        data.create_features_to_plot()
        # data.slice_dataframe()
        data.fig_boxes(open(options.abox_file), open(options.bbox_file))

    if options.output_files == "termination_valleys":
        data.create_features_to_plot()
        data.slice_dataframe()
        data.termination_efficency_valleys()

    if options.output_files == "termination":
        data.create_features_to_plot()
        data.slice_dataframe()
        data.termination_efficency()

    print '# Done.'
main()