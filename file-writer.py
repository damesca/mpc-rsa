import sys

print "---FILE-WRITER---"

f = open(sys.argv[1], "w+")
f.write(sys.argv[2] + "\n")
f.write(sys.argv[3] + "\n")
f.close()

