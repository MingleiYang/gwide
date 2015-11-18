#!/usr/bin/env python
__author__ = 'Tomasz Turowski'
__copyright__	= "Copyright 2015"
__version__		= "1.0"
__credits__		= ["Tomasz Turowski"]
__email__		= "twturowski@gmail.com"
__status__		= "Production"

import gwide.methods as gtk
from gwide.gwidePlot_class import *
import argparse
from argparse import RawTextHelpFormatter
import os

""" Script working with concat file generated by pileupsToConcat.py script. Read concat file and according to options.
Can plot intron, and peaks found by pypeaks script."""

#setup option parser
usage = "Usage: prints genom wide plot, for genes 'as you wish' and aligned 'as you wish'"
parser = argparse.ArgumentParser(usage=usage, formatter_class=RawTextHelpFormatter)
files = parser.add_argument_group('Options for input files')
files.add_argument("-g", "--gtf_file", dest="gtf_file", help="Provide the path to your gtf file.",
                 type=str, default=None)
files.add_argument("-c", "--concat_file", dest="concat_file", help="Provide the path to your concat file. Required.",
                 metavar="FILE", default=None, required=True)
files.add_argument("--5flank", dest="five_prime_flank", type=int, help="Set up 5 prime flank in pileup file. Default = 250", default=250)
files.add_argument("--3flank", dest="three_prime_flank", type=int, help="Set up 3 prime flank in pileup file. Default = 250", default=250)
files.add_argument("-l", "--list_file", dest="list_file", help="Provide the path to your (tab) file genes.list. Only listed genes will be plotted. Can be aligned as second column",
                 type=str)
peaks = parser.add_argument_group('Option for peaks finder (pypeaks')
peaks.add_argument("--lookahead", dest="lookahead", type=int, help="Set up lookahead parameter for pypeaks function. Default = 20", default=20)
universal = parser.add_argument_group('Universal options')
universal.add_argument("-t", "--hits_threshold", dest="hits_threshold", type=int, help="Set up threshold for pileup. Default 100 reads",
                  default=0)
universal.add_argument("-r", "--readthrough", dest="readthrough", type=int, help="Set up when readthrough should start countin. Default: 15",
                  default=15)
universal.add_argument("-n", "--normalized", dest="normalized", action="store_true", help="to work on data normalized 'reads per Milion'. Default: False", default=False)
output = parser.add_argument_group('Options for output files')
output.add_argument("-p", "--prefix", dest="out_prefix", type=str, help="Prefix for output files. Default to standard output. Not supported for -o ratio.", default=None)
output.add_argument("-o", "--output", dest="output", choices=["std", "aligner", "RTend", "ratio", "makeRTGTF"], help="Select from following options:"+'\n\n'
                   "std - 5` and 3` end aligned only"+'\n'
                    "aligner - std plus chosen aligner (-l option)"+'\n'
                    "ratio - plot gwideToolkit ratio a exp / b exp"+'\n'
                    "RTend - std and aligned to 3` end of read-through (-l option). -e works to choose experiment to align and filter"+'\n', default="std")
special = parser.add_argument_group('Special options for some -o choices')
special.add_argument("--ntotal", dest="ntotal", action="store_true", help="Normalize to sum of all reads (sum = 1). Default: False", default=False)
special.add_argument("--nmax", dest="nmax", action="store_true", help="Normalize to maximal value (max = 1). Default: False", default=False)
special.add_argument("-s", "--set_up", dest="set_up", type=float, help="Set up factor threshold (for -o gwideToolkit only)",
                  default=None)
special.add_argument("-f", dest="filter", type=str, help="Filter in results factor_above_value; type i.e. RT_above_0.25 or a_below_1.5. To chose: RT, a, b, i, e, f, intron")
special.add_argument("-e", dest="experiment", type=str, help="Filter according to values from one experiment only", default=None)
special.add_argument("-a", dest="to_divide", type=str, help="experiment to divide by -b (-o ratio)",
                  default=None)
special.add_argument("-b", dest="divisor", type=str, help="experiment being divisor for -a (-o ratio)", default=None)
special.add_argument("--select", dest="select", type=str, help="To print additional plot with selecter area and no titles keep form 200_300 (range from 200 to 300)", default=None)
options = parser.parse_args()

gtf_file = gtk.getGTF(options.gtf_file)
concat_file = options.concat_file
list_file = options.list_file

#preparing naming of output files
if options.out_prefix:
    prefix = options.out_prefix+'_'
    filename = options.out_prefix+'_rt'+str(options.readthrough)+'_l'+str(options.lookahead)+'_t'+str(options.hits_threshold)+'.list'
else:
    prefix = str()
    filename = 'rt'+str(options.readthrough)+'_l'+str(options.lookahead)+'_t'+str(options.hits_threshold)+'.list'
if options.normalized == True:
    prefix = 'normalized_'+prefix

data = GenomeWidePlot(gtf_file=gtf_file, five_prime_flank=options.five_prime_flank, readthrough_start=options.readthrough,
                      three_prime_flank=options.three_prime_flank, hits_threshold=options.hits_threshold, lookahead=options.lookahead,
                      prefix=prefix, normalized=options.normalized)

#setting up dependencies
if options.output == "ratio":
    options.normalized = True

#reading csv file
data.read_csv(concat_file)

#plotting
if options.output == 'std':
    data.calculate(details=True, ntotal=False, nmax=False)
    data.std(filter=options.filter, experiment_to_filter=options.experiment)

if options.output == 'aligner':
    if not list_file:
        print "Please provide path how to align files using -l file.list"
    else:
        data.calculate(details=True, ntotal=False, nmax=False)
        data.read_list(list_file)
        data.aligner(file=os.path.basename(list_file), filter=options.filter, experiment_to_filter=options.experiment)

if options.output == 'RTend':
    data.calculate(details=True, ntotal=False, nmax=False)
    data.RT_aligner(filter=options.filter, experiment_to_align=options.experiment)

if options.output == "ratio":
    data.calculate(details=False, ntotal=True, nmax=True)
    if options.ntotal == True:
        data.ratio(to_divide=options.to_divide, divisor=options.divisor, exp_to_use='_ntotal', filter=options.filter)
        if options.select:
            data.ratio(to_divide=options.to_divide, divisor=options.divisor, exp_to_use='_ntotal', select=options.select, filter=options.filter)
    if options.nmax == True:
        data.ratio(to_divide=options.to_divide, divisor=options.divisor, exp_to_use='_nmax', filter=options.filter)
    data.ratio(to_divide=options.to_divide, divisor=options.divisor, filter=options.filter)

if options.output == "makeRTGTF":
    data.find_peaks()
    # data.calculate(details=False, ntotal=True, nmax=True)
    data.makeRTGTF()


print '# Done.'

