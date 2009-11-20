# Build JSON Template docs

default: jesyll-doc

# TODO: Need correct dependencies
examples: 
	cp ../python/examples/*.py .

__ODM-TOC.html: 
	./extract_toc.py On-Design-Minimalism.html.jsont > __ODM-TOC.html

testTableExample-01.html:
	cp ../test-cases/testTableExample-01.html .

jesyll-doc: examples __ODM-TOC.html testTableExample-01.html
	./jesyll.sh

