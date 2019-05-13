#!/usr/bin/python3

import re
import subprocess
import sys

# Make sure there are the right number of arguments.
# TODO: Check formatting etc.
if not len( sys.argv ) == 2:
  print( "Usage: python3 pin_extract.py <datasheet.pdf>" )
  sys.exit( 1 )

# Run 'pdftotext' on the datasheet.
txt_fn = sys.argv[ 1 ].replace( ".pdf", ".txt" ).replace( "../", "" )
subprocess.run( "pdftotext -layout -nopgbrk {0} {1}".format( sys.argv[ 1 ], txt_fn ), shell = True, check = True )

# Open the resulting text file.
txt_file = open( txt_fn, "r", encoding = "utf-8" )

# Copy the transcribed pinouts into an array of lines.
DISCARDING = 0
PENDING = 1
COPYING = 2
PAUSED = 3
parse_state = DISCARDING
table_lines = []
# The first line of the table includes the start of
# the column header, (function upon reset).
start_key = "(function"
# We can ignore headers and footers.
#mid_break_key = "DocID"
mid_break_key = "Rev "
# The last line contains footnotes.
end_key = "1. "

# The datasheet is a big document; process it line-by-line.
for line in txt_file:
  if parse_state == DISCARDING:
    if start_key in line:
      parse_state = PENDING
  elif parse_state == PENDING:
    if line.strip() == "":
      parse_state = COPYING
  elif parse_state == COPYING:
    if mid_break_key in line:
      parse_state = PAUSED
    elif line.startswith( end_key ):
      parse_state = DISCARDING
      break
    else:
      if not line.strip() == "":
        table_lines.append( line )
  elif parse_state == PAUSED:
    if start_key in line:
      parse_state = PENDING

# We're done with the original transcription now. Close the file.
txt_file.close()

# Debug: Write the resulting lines to a new file.
'''
parsed_table_file = open( "mid_{0}".format( txt_fn ), "w" )
for line in table_lines:
  parsed_table_file.write( line )
parsed_table_file.close()
'''

# Parse each line into an array. This is slightly tricky because
# the pdf utility parses each table row into several text rows,
# and the row marking the pin number is often in the middle
# of the table row instead of the top or bottom.
# So. Step 1. Find the table column boundaries. A column is
# marked by two or more spaces.
# First, replace all single spaces in each line with the '|' character,
# which seems to be unused by ST's pinout charts.
temp_lines = []
for line in table_lines:
  sline = line.strip()
  tline = ""
  paren = False
  for i in range( len( sline ) ):
    # Don't copy parentheticals; datasheet shouldn't have nested ones.
    if sline[ i ] == ")":
      paren = False
    elif sline[ i ] == "(":
      paren = True
    elif paren:
      paren = True
    elif sline[ i ] == " ":
      # 'i' will never be the first or last character because of the strip() call above.
      if sline[ i + 1 ] != " " and sline[ i - 1 ] != " ":
        tline = tline + "|"
      else:
        tline = tline + " "
    else:
      tline = tline + sline[ i ]
  # Second, replace all instances of multiple spaces with a single space,
  # as long as there are instances of multiple spaces.
  while "  " in tline:
    tline = tline.replace( "  ", " " )
  tline = tline.strip()
  # Third, replace spaces with '#' characters. These look like they are unused
  # in the datasheet tables (unlike commas), so I'll use them as delimiters.
  tline = tline.replace( " ", "#" )
  # Fourth, replace the temporary '|' characters with spaces again.
  tline = tline.replace( "|", " " )
  if not tline == "":
    temp_lines.append( tline + "\r\n" )

# Debug: Write the resulting lines to a new file.
parsed_table_file = open( "mid_{0}".format( txt_fn ), "w" )
for line in temp_lines:
  parsed_table_file.write( line )
parsed_table_file.close()

# TODO: Figure out how to reliably parse these lines :(
# For now, at least this saves a lot of time.
print( "Midpoint printed. Sorry, I can't figure out how to parse it:" )
print( "mid_{0}".format( txt_fn ) )
print( "Please correct the formatting, and then run 'pin_ingest.py mid_{0} <pin_column>'.".format( txt_fn ) )
print( "The correct format is: [N]#[N]#[N]#...#[Pin Name]#[Type1]#[Type2]#-#[periph,periph,periph...]" )
print( "Where '[N]' represents the pin number for a given chip package." )
