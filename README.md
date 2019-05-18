# STM32 Pin definition generator.

I wanted to make SVG visualizations of STM32 pinouts, and ST doesn't seem to distribute CSV files with peripheral information. I mean, they might, but I couldn't find any. So this is an attempt to pull the information out of their PDF datasheets.

Unfortunately, the formatted output from `pdftotext` is a little tricky to parse, so you still have to manually put peripheral labels on the right rows and clean up the column boundaries. Still, it's a lot faster than doing the whole thing by hand.

The parsing might also break with certain datasheets; I haven't tried too many. The formatting will also only work for QFP/QFN/TSSOP packages. BGA/WLCSP packages use alphanumeric identifiers which the script will try to parse as integers. What I'm trying to say is, this is not very complete or easy-to-use. Sorry.

# Usage

There are two scripts. The `pin_extract.py` script pulls a pin table out of an STM32 datasheet, and stores it in an intermediary text file. The datasheets use commas for peripheral separators, so '#' characters are used to separate columns in the text file.

The intermediary file will have a bunch of peripheral definitions on their own lines - usually ones without trailing commas mark pin boundaries, but it is not entirely consistent. The script will print out the exact format that it wants to see when it finishes running.

Once the intermediary file is re-formatted, the `pin_ingest.py` script will parse it into two LaTeX files designed to go on the top and bottom of a vector image of which peripherals go to which pins on the chip. Since ST's datasheets usually cover several similar chips, the `pin_ingest.py` script accepts two arguments: the input file, and which (0-indexed) column of the 'pin mapping' table you want to generate tables for.

Examples of processed intermediary files are provided under the `examples/` directory.

Inkscape can import the PDF files generated by `pdflatex`, and I assume that Photoshop & co. can too. The cells are colored based on a peripheral's number, and peripherals are grouped into individual rows by protocol (USART, SPI, Timers, etc).

# Tabula

A better option is to use an excellent open-source project called Tabula to create a CSV file of the table. There is also a `pin_tabula_ingest.py` script for processing those files, and it has the same syntax as `pin_ingest.py`:

    pin_tabula_ingest.py <tabula_export>.csv <pin_column>

It generates the same LaTeX files as the other scripts, but without the tedious manual processing.

# Example

<img src="./examples/STM32L031Gx.svg">
