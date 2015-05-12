# Switched this back to bibtex because the current version of crosstex
# seems to have a bug causing incorrect capitalization in the titles.

LATEX=pdflatex
TEXFLAGS=

TARGET=serpent_tutorial.pdf 

all: $(TARGET)

$(TARGET): $(TARGET:.pdf=.tex) *.tex *.bib Makefile
	$(LATEX) -shell-escape $(TEXFLAGS) $<
	bibtex $(basename $<)
	$(LATEX) -shell-escape $(TEXFLAGS) $<
	$(LATEX) -shell-escape $(TEXFLAGS) $<

	$(LATEX) -shell-escape $(TEXFLAGS) how_to_program_a_safe_smart_contract.tex
	bibtex $(basename $<)
	$(LATEX) -shell-escape $(TEXFLAGS) how_to_program_a_safe_smart_contract.tex 
	$(LATEX) -shell-escape $(TEXFLAGS) how_to_program_a_safe_smart_contract.tex

test: test-fonts test-info

test-fonts: $(TARGET)
	pdffonts $<

test-info: $(TARGET)
	pdfinfo $<

print: $(TARGET)
	pdftops $< - | lpr -P lws510

view: $(TARGET)
	kpdf $<

clean:
	rm -f $(TARGET) *.log *.aux *.bbl *.blg *.bak *.toc *.out .*.xtx.cache parsetab.py \#*\# *~
