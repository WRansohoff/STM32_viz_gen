#!/usr/bin/python3

import math
import latex_strs
from latex_strs import *
import re
import subprocess
import sys

# Make sure there are the right number of arguments.
# TODO: Check formatting etc.
if not len( sys.argv ) == 3:
  print( "Usage: python3 pin_ingest.py <file.txt> <pin_column>" )
  sys.exit( 1 )

# Gather arguments.
txt_fn = sys.argv[ 1 ]
pin_col = int( sys.argv[ 2 ] )

# Read the input file. 
f = open( txt_fn, "r" )
pin_lines = f.readlines()
f.close()

# Parse the table rows.
pin_rows = []
for i in range( len( pin_lines ) ):
  pin_rows.append( None )
for line in pin_lines:
  row = line.strip().split( "#" )
  # Only append pins that are on the selected package.
  if not row[ pin_col ] == "-":
    # TODO: BGA packages use alphanumeric.
    pin_num = int( row[ pin_col ] )
    pin_rows[ pin_num ] = {
      "name":  row[ len( row ) - 5 ],
      "type1": row[ len( row ) - 4 ],
      "type2": row[ len( row ) - 3 ],
      "peripherals": row[ len( row ) - 1 ].split( "," ),
    }
    # DEBUG: Print out imported rows.
    #print( pin_rows[ pin_num ] )

# Figure out how many peripherals there are to deal with.
temp_periphs = []
for row in pin_rows:
  if not row:
    continue
  periph_row = {
    "Name":        row[ "name" ],
    "I2C":         [],
    "SPI/I2S":     [],
    "USART":       [],
    "USB/PD":      [],
    "ADC/DAC":     [],
    "Timers":      [],
    "Comparators": [],
    "Op-Amps":     [],
    "Other":       [],
  }
  for periph in row[ "peripherals" ]:
    if "I2C" in periph:
      periph_row[ "I2C" ].append( periph )
    elif "SPI" in periph or "I2S" in periph:
      periph_row[ "SPI/I2S" ].append( periph )
    elif "USART" in periph or "UART" in periph or "LPUART" in periph:
      periph_row[ "USART" ].append( periph )
    elif "USB" in periph or "UCPD" in periph or "OTG" in periph:
      periph_row[ "USB/PD" ].append( periph )
    elif "ADC" in periph or "DAC" in periph:
      periph_row[ "ADC/DAC" ].append( periph )
    elif "TIM" in periph or "LPTIM" in periph:
      periph_row[ "Timers" ].append( periph )
    elif "COMP" in periph:
      periph_row[ "Comparators" ].append( periph )
    # TODO: Op-Amps
    else:
      # Ignore some common values.
      if periph != "EVENTOUT":
        periph_row[ "Other" ].append( periph )
  temp_periphs.append( periph_row )
  # Debug: Print out peripheral rows.
  #print( "{0:d}: Periphs: {1}".format( len( temp_periphs ), periph_row ) )

# Only include peripherals which are actually used.
periphs_to_use = [ "Name" ]
for row in temp_periphs:
  for k, v in row.items():
    if not k in periphs_to_use:
      if len( v ) > 0:
        periphs_to_use.append( k )

# Debug: Print out which peripherals to use.
#print( "\r\n{0}".format( periphs_to_use ) )

# Gather used peripherals.
periphs = []
for row in temp_periphs:
  new_periph = {}
  for k, v in row.items():
    if k in periphs_to_use:
      new_periph[ k ] = v
  periphs.append( new_periph )

# Find out maximum height of each peripheral row for each half.
tlen = int( len( periphs ) / 2 )
periphs_max_1h = { "Name": 2 }
periphs_max_2h = { "Name": 2 }
for row in range( tlen ):
  for k, v in periphs[ row ].items():
    if k == "Name":
      continue
    if len( v ) > 0:
      if not k in periphs_max_1h:
        periphs_max_1h[ k ] = len( v )
      elif periphs_max_1h[ k ] < len( v ):
        periphs_max_1h[ k ] = len( v )
for row in range( tlen ):
  for k, v in periphs[ len( periphs ) - ( row + 1 ) ].items():
    if k == "Name":
      continue
    if len( v ) > 0:
      if not k in periphs_max_2h:
        periphs_max_2h[ k ] = len( v )
      elif periphs_max_2h[ k ] < len( v ):
        periphs_max_2h[ k ] = len( v )
for val in periphs_to_use:
  if not val in periphs_max_1h:
    periphs_max_1h[ val ] = 1
  if not val in periphs_max_2h:
    periphs_max_2h[ val ] = 1

# Debug: Print the maximum row heights for each table.
#print( "T1: {0}\r\nT2: {1}\r\n".format( periphs_max_1h, periphs_max_2h ) )

# Method to translate peripheral labels into their
# acronym shorthands.
def types_from_str( pstr ):
  if pstr == "I2C":
    return [ "I2C" ]
  elif pstr == "SPI/I2S":
    return [ "SPI", "I2S" ]
  elif pstr == "USART":
    return [ "USART", "LPUART", "UART" ]
  elif pstr == "USB/PD":
    return [ "USB", "OTG", "UCPD" ]
  elif pstr == "ADC/DAC":
    return [ "ADC", "DAC" ]
  elif pstr == "Timers":
    return [ "LPTIM", "TIM" ]
  elif pstr == "Comparators":
    return [ "COMP" ]
  elif pstr == "Other":
    return [ "RTC_TAMP", "WKUP" ]
  # TODO: Op-Amps
  else:
    return []

# Method to get an empty cell with color of a given peripheral.
def cell_color_for( cell_str, cell_types = None ):
  # Special cases:
  # Debugging pins.
  if cell_str == "SWCLK" or cell_str == "SWDIO":
    return "\\tcpE"
  # 'MCO' clock output pin.
  if cell_str == "MCO":
    return "\\tcpF"
  # Infrared LED output pin.
  if cell_str == "IR_OUT":
    return "\\tcpD"
  # Oscillator pins.
  if "OSC_" in cell_str or "OSC32_" in cell_str:
    return "\\tcpC"
  # 'Boot' pin[s].
  if "Boot" in cell_str:
    return "\\tcpF"
  # 'Reset' pin.
  if "Reset" in cell_str:
    return "\\tcpE"
  # Digital/Analog power supply pins.
  if "power" in cell_str:
    return "\\tcpD"
  # Ground pins.
  if "Ground" in cell_str or "ground" in cell_str:
    return "\\tcpC"
  # Voltage reference pins.
  if "VREF_" in cell_str:
    return "\\tcpD"
  # Standard peripherals:
  if cell_types:
    for cell_type in cell_types:
      if "{0}10".format( cell_type ) in cell_str:
        return "\\tcpD"
      elif "{0}11".format( cell_type ) in cell_str:
        return "\\tcpE"
      elif "{0}12".format( cell_type ) in cell_str:
        return "\\tcpF"
      elif "{0}13".format( cell_type ) in cell_str:
        return "\\tcpA"
      elif "{0}14".format( cell_type ) in cell_str:
        return "\\tcpB"
      elif "{0}15".format( cell_type ) in cell_str:
        return "\\tcpC"
      elif "{0}16".format( cell_type ) in cell_str:
        return "\\tcpD"
      elif "{0}17".format( cell_type ) in cell_str:
        return "\\tcpE"
      elif "{0}18".format( cell_type ) in cell_str:
        return "\\tcpF"
      elif "{0}19".format( cell_type ) in cell_str:
        return "\\tcpA"
      elif "{0}20".format( cell_type ) in cell_str:
        return "\\tcpB"
      elif "{0}21".format( cell_type ) in cell_str:
        return "\\tcpC"
      elif "{0}22".format( cell_type ) in cell_str:
        return "\\tcpD"
      elif "{0}23".format( cell_type ) in cell_str:
        return "\\tcpE"
      elif "{0}1".format( cell_type ) in cell_str:
        return "\\tcpA"
      elif "{0}2".format( cell_type ) in cell_str:
        return "\\tcpB"
      elif "{0}3".format( cell_type ) in cell_str:
        return "\\tcpC"
      elif "{0}4".format( cell_type ) in cell_str:
        return "\\tcpD"
      elif "{0}5".format( cell_type ) in cell_str:
        return "\\tcpE"
      elif "{0}6".format( cell_type ) in cell_str:
        return "\\tcpF"
      elif "{0}7".format( cell_type ) in cell_str:
        return "\\tcpA"
      elif "{0}8".format( cell_type ) in cell_str:
        return "\\tcpB"
      elif "{0}9".format( cell_type ) in cell_str:
        return "\\tcpC"
      elif "{0}0".format( cell_type ) in cell_str:
        return "\\tcpE"
      elif "{0}".format( cell_type ) in cell_str:
        return "\\tcpA"
  # Other special cases.
  # Misc. RTC pins.
  if "RTC_" in cell_str:
    return "\\tcpE"
  return "\\tcna"

# Method to get a table cell color for a given peripheral.
# There are 6 colors, A-F.
def cell_color( cell_str, raised, cell_types = None ):
  rstr = ""
  if raised:
    rstr = "up"
  return "{0}{1}{{{2}}}".format( cell_color_for( cell_str, cell_types ), rstr, cell_str )

# Method to write a table cell, given a list of peripherals,
# a target peripheral type, and cell heights.
# Note: This will truncate cells if there are too many values.
def table_cell_str( periphs, periph_type, cur_h, max_h ):
  # If there are no peripherals, print 'N/A' text.
  if len( periphs ) == 0:
    if cur_h == int( max_h / 2 ):
      if max_h % 2 == 0:
        return "\\tcnaup{N/A}"
      else:
        return "\\tcna{N/A}"
    else:
      return "\\tcna{}"
  # How large is each 'slot'?
  slsize = int( math.ceil( float( max_h ) / float( len( periphs ) ) ) )
  # Which 'slot' are we on?
  slind = int( cur_h / slsize )
  # How far along the 'slot' are we?
  slprog = cur_h % slsize
  # If this is the last 'slot', does it need shrinking?
  if max_h % slsize != 0 and slind == int( max_h / slsize ):
    slsize = max_h - int( max_h / slsize ) * slsize
  # Should this slot contain text? (Is this the H. center?)
  should_text = ( int( slsize / 2 ) == slprog )
  should_raise = ( ( slsize % 2 ) == 0 )
  if should_text:
    return cell_color( periphs[ slind ], should_raise, types_from_str( periph_type ) ).replace( "_", "\_" )
  else:
    return "{0}{{}}".format( cell_color_for( periphs[ slind ], types_from_str( periph_type ) ).replace( "_", "\_" ) )

# Write a table row. To avoid using globals:
# p = periphs
# p1h = periphs_max_1h
# p2h = periphs_max_2h
# ptu = periphs_to_use
def write_table_row( p, p1h, p2h, ptu, periph_type ):
  if periph_type in ptu:
    # Label columns.
    if p1h[ periph_type ] == 1:
      t1f.write( "\\textbf{{{0}}}\n".format( periph_type ) )
    else:
      t1f.write( "\\multirow{{{0:d}}}{{*}}{{\\textbf{{{1}}}}}".format( p1h[ periph_type ], periph_type ) )
    if p2h[ periph_type ] == 1:
      t2f.write( "\\textbf{{{0}}}\n".format( periph_type ) )
    else:
      t2f.write( "\\multirow{{{0:d}}}{{*}}{{\\textbf{{{1}}}}}".format( p2h[ periph_type ], periph_type ) )
    # Individual pins.
    for i in range( p1h[ periph_type ] ):
      for j in range( tlen ):
        t1f.write( "& {0} ".format( table_cell_str( p[ j ][ periph_type ], periph_type, i, p1h[ periph_type ] ) ) )
      t1f.write( " \\\\\n" )
    t1f.write( "\\hline\n" )
    for i in range( p2h[ periph_type ] ):
      for j in range( tlen ):
        t2f.write( "& {0} ".format( table_cell_str( p[ len( p ) - ( j + 1 ) ][ periph_type ], periph_type, i, p2h[ periph_type ] ) ) )
      t2f.write( " \\\\\n" )
    t2f.write( "\\hline\n" )

# Generate the table. We have static strings to define
# LaTeX formatting commands and table start/end, but
# we need to populate the actual layout and rows/columns.
# There will be 2 tables, top/bottom, each with half of the
# package's pins and an extra column for labels.
# Both tables will have one row for each 'periphs_to_use' entry.
# Table 1: Pin names on top.
t1f = open( txt_fn.replace( ".txt", "_t1.tex" ), "w" )
t2f = open( txt_fn.replace( ".txt", "_t2.tex" ), "w" )
t1f.write( doc_start )
t2f.write( doc_start )
t1f.write( doc_table_start )
t2f.write( doc_table_start )
# Write column layout; ( # pins / 2 ) + 1.
t1f.write( "l" )
t2f.write( "l" )
for i in range( tlen ):
  t1f.write( "|c" )
  t2f.write( "|c" )
t1f.write( "}\n" )
t2f.write( "}\n" )
# Write the Table 1 'Pin Name' row on top.
t1f.write( "\\multirow{2}{*}{\\textbf{Pin Name}} " )
for i in range( tlen ):
  t1f.write( "& " )
t1f.write( "\\\\\n" )
for i in range( tlen ):
  t1f.write( "& \\uprb{{{0}}}".format( periphs[ i ][ "Name" ].replace( "_", "\_" ) ) )
t1f.write( "\\\\\n\\hline\n" )
# TODO: Make an iterable object for periph names.
# Write the 'I2C' rows, if applicable.
write_table_row( periphs, periphs_max_1h, periphs_max_2h, periphs_to_use, "I2C" )
# Write the 'SPI' rows, if applicable.
write_table_row( periphs, periphs_max_1h, periphs_max_2h, periphs_to_use, "SPI/I2S" )
# Write the 'USART' rows, if applicable.
write_table_row( periphs, periphs_max_1h, periphs_max_2h, periphs_to_use, "USART" )
# Write the 'USB / Power Delivery' rows, if applicable.
write_table_row( periphs, periphs_max_1h, periphs_max_2h, periphs_to_use, "USB/PD" )
# Write the 'ADC/DAC' rows, if applicable.
write_table_row( periphs, periphs_max_1h, periphs_max_2h, periphs_to_use, "ADC/DAC" )
# Write the 'Timer' rows, if applicable.
write_table_row( periphs, periphs_max_1h, periphs_max_2h, periphs_to_use, "Timers" )
# Write the 'Comparator' rows, if applicable.
write_table_row( periphs, periphs_max_1h, periphs_max_2h, periphs_to_use, "Comparators" )
# TODO: Op-Amps
# Write the 'Other' rows.
write_table_row( periphs, periphs_max_1h, periphs_max_2h, periphs_to_use, "Other" )
# Write the Table 2 'Pin Name' row on bottom.
t2f.write( "\\multirow{2}{*}{\\textbf{Pin Name}} " )
for i in range( tlen ):
  t2f.write( "& " )
t2f.write( "\\\\\n" )
for i in range( tlen ):
  t2f.write( "& \\uprb{{{0}}}".format( periphs[ len( periphs ) - ( i + 1 ) ][ "Name" ].replace( "_", "\_" ) ) )
t2f.write( "\\\\\n\\hline\n" )
# Done; write closing logic.
t1f.write( doc_table_end )
t2f.write( doc_table_end )
t1f.close()
t2f.close()
