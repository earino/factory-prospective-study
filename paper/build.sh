#!/bin/sh
set -eu
cd "$(dirname "$0")/draft"
mkdir -p ../output
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../output main.tex > ../output/build-pass1.txt
(cd ../output && BIBINPUTS=../draft: BSTINPUTS=../draft: bibtex main > build-bibtex.txt)
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../output main.tex > ../output/build-pass2.txt
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../output main.tex > ../output/build-pass3.txt
cp ../output/main.pdf ../output/paper.pdf
