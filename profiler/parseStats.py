import profile
import pstats
import sys

statfile = sys.argv[1]
# Read all 5 stats files into a single object
stats = pstats.Stats(statfile)
#for i in range(1, 5):
#    stats.add('profile_stats_%d.stats' % i)

# Clean up filenames for the report
stats.strip_dirs()

# Sort the statistics by the cumulative time spent in the function
stats.sort_stats('cumulative')

stats.print_stats(30)
stats.print_callees()

