all: jsontemplate.jar jsontemplate_test.jar 

jsontemplate.jar: jsontemplate/*.java 
	rm -rf classes
	mkdir classes
	rm -f jsontemplate.jar
	javac -d classes -Xlint:unchecked -g $^
	jar cf jsontemplate.jar -C classes jsontemplate

jsontemplate_test.jar: jsontemplate_test/*.java  jsontemplate_test/org/json/*.java
	rm -rf testclasses
	mkdir testclasses
	rm -f jsontemplate_test.jar
	javac -d testclasses -Xlint:unchecked -g $^
	jar cf jsontemplate_test.jar -C testclasses jsontemplate_test

clean:
	rm -f jsontemplate.jar jsontemplate_test.jar
	rm -rf classes testclasses
