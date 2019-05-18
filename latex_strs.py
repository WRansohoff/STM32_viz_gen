# Define some common strings for the LaTeX table files.

doc_start = '''
\\documentclass{article}
\\usepackage{multirow}
\\usepackage[table]{xcolor}
\\usepackage{tikz}
\\usepackage{tgheros}
% The default underscores are very short :/
\\renewcommand{\\_}[0]{\\rule{5pt}{1pt}}
% Use sans-serif font by default.
\\renewcommand{\\familydefault}{\\sfdefault}
% Convenience commands for table styling.
\\newcommand{\\upr}[1]{\\raisebox{0.5em}[0.5em][0em]{#1}}
\\newcommand{\\upri}[1]{\\upr{\\textit{#1}}}
\\newcommand{\\uprb}[1]{\\upr{\\textbf{#1}}}
% Styling for 'N/A' cells.
\\newcommand{\\tcna}[1]{\\cellcolor[HTML]{CCCCCC} \\textit{#1}}
\\newcommand{\\tcnaup}[1]{\\tcna{\\upri{#1}}}
% Styling for peripheral cells.
\\newcommand{\\tcpA}[1]{\\cellcolor[HTML]{2EF43F} #1}
\\newcommand{\\tcpAup}[1]{\\upr{\\cellcolor[HTML]{2EF43F} #1}}
\\newcommand{\\tcpB}[1]{\\cellcolor[HTML]{EF7CD8} #1}
\\newcommand{\\tcpBup}[1]{\\upr{\\cellcolor[HTML]{EF7CD8} #1}}
\\newcommand{\\tcpC}[1]{\\cellcolor[HTML]{1DABE2} #1}
\\newcommand{\\tcpCup}[1]{\\upr{\\cellcolor[HTML]{1DABE2} #1}}
\\newcommand{\\tcpD}[1]{\\cellcolor[HTML]{E83030} #1}
\\newcommand{\\tcpDup}[1]{\\upr{\\cellcolor[HTML]{E83030} #1}}
\\newcommand{\\tcpE}[1]{\\cellcolor[HTML]{C8EA1E} #1}
\\newcommand{\\tcpEup}[1]{\\upr{\\cellcolor[HTML]{C8EA1E} #1}}
\\newcommand{\\tcpF}[1]{\\cellcolor[HTML]{F2840E} #1}
\\newcommand{\\tcpFup}[1]{\\upr{\\cellcolor[HTML]{F2840E} #1}}
% Set page dimensions.
\\usepackage[paperwidth=250em, paperheight=35em,
            top=5em, bottom=0em, left=0em, right=0em]{geometry}
'''

doc_table_start = '''
\\begin{document}
\\pagenumbering{gobble}

\\begin{table}[h!]
  \\begin{center}
    \\begin{tikzpicture}
      \\node (table) [inner sep=0pt] {
        \\begin{tabular}{'''

doc_table_end = '''
        \\end{tabular}
      };
      \\draw [rounded corners=0.5em]
        (table.north west) rectangle (table.south east);
    \\end{tikzpicture}
  \\end{center}
\\end{table}

\\end{document}
'''
