@echo off
rem Run standalone JavaScript tests
rem 
rem Load the test framework, then JSON Template, then the tests

cscript //Nologo javascript\cscript-shell.js javascript\jsunity-0.6.js javascript\json-template.js javascript\json-template-test.js
