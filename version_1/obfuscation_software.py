#!/usr/bin/python

import os
import glob
import shutil
import sys, getopt
from awesome_print import ap
from obfuscation_lib import *

def main(argv):
   input_corpus_directory = ''
   output_corpus_directory = ''
   try:
      print(argv)
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'Usage is: python obfuscation_software.py -i <input_corpus_directory> -o <output_corpus_directory>'
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-i", "--ifile"):
         input_corpus_directory = arg
      elif opt in ("-o", "--ofile"):
         output_corpus_directory = arg

   problem_directories = glob.glob(  os.path.join(input_corpus_directory, "*")  )

   if(os.path.exists(output_corpus_directory)):
      shutil.rmtree(output_corpus_directory)
   os.mkdir(output_corpus_directory)      

   for problem_directory in problem_directories:
      problem_name = os.path.basename(problem_directory)
      ap("In problem:  {0}".format(problem_name))
      os.mkdir( os.path.join(output_corpus_directory, problem_name) )
      output_file_path = os.path.join( output_corpus_directory, problem_name, "obfuscated.json" )       
      obfuscate_author(problem_directory, output_file_path)
      ap("Completed problem:  {0}".format(problem_name))

if __name__ == "__main__":
   main(sys.argv[1:])