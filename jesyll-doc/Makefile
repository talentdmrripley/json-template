# Build JSON Template docs

default: jesyll-doc

# TODO: Need correct dependencies
examples: 
	cp ../python/examples/*.py .

__ODM-TOC.html: 
	./extract_toc.py On-Design-Minimalism.html.jsont > __ODM-TOC.html

jesyll-doc: examples __ODM-TOC.html
	./jesyll.sh

