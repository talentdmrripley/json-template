# Build JSON Template docs
#
# TODO: This should probably run from the root

default: jesyll-doc

# TODO: Need correct dependencies
examples: 
	cp ../python/examples/*.py .

__ODM-TOC.html: 
	./extract_toc.py On-Design-Minimalism.html.jsont > __ODM-TOC.html

# This one is included directly in an article
testTableExample-01.html:
	cp ../test-cases/testTableExample-01.html .

# This one is just served plain
testTableExample-01.js.html:
	cp ../test-cases/testTableExample-01.js.html .

jesyll-doc: examples __ODM-TOC.html testTableExample-01.html
	./jesyll.sh

