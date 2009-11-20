<?php

require_once 'PHPUnit/Framework.php';
require_once dirname(__FILE__)."/jsontemplate.php";

class JsonTemplateTests
{
    public static function suite()
    {
        $suite = new PHPUnit_Framework_TestSuite('Json Template PHP');
        $suite->addTestSuite('JsonTemplateTokenizeTest');
        $suite->addTestSuite('JsonTemplateFromStringTest');
        $suite->addTestSuite('JsonTemplateJsonTest');
        $suite->addTestSuite('JsonTemplateTemplateTest');
        return $suite;
    }
}

class JsonTemplateTokenizeTest extends PHPUnit_Framework_TestCase
{
	function testMakeTokenRegex()
	{
		$token_re = JsonTemplateModule::pointer()->MakeTokenRegex('[',']');
		$text = "
[# Comment#]

[# Comment !@#234 with all ...\\\ sorts of bad characters??]

[# Multi ]
[# Line ]
[# Comment ]
text
[!!]
text

[foo|fmt]
[bar|fmt]";

		$tokens = preg_split($token_re,$text, -1, PREG_SPLIT_DELIM_CAPTURE);
		$this->assertEquals(17,count($tokens));

	}

	function testSectionRegex()
	{
		# Section names are required
		$this->assertEquals(preg_match(JsonTemplateModule::pointer()->section_re,'section'),0);
		$this->assertEquals(preg_match(JsonTemplateModule::pointer()->section_re,'repeated section'),0);

		preg_match(JsonTemplateModule::pointer()->section_re,'section Foo',$match);
		$this->assertEquals($match,array('section Foo','','section','Foo'));

		preg_match(JsonTemplateModule::pointer()->section_re,'repeated section @',$match);
		$this->assertEquals($match,array('repeated section @','repeated','section','@'));
	}
}

class JsonTemplateFromStringTest extends PHPUnit_Framework_TestCase
{
	function testEmpty()
	{
		$s =  "Format-Char: |
Meta: <>
";
		$t = JsonTemplateModule::pointer()->FromString($s);
		$this->assertEquals($t->template_str,'');
		$this->assertEquals($t->compile_options['format_char'],'|');
		$this->assertEquals($t->compile_options['meta'],'<>');

		# Empty template
		$t = JsonTemplateModule::pointer()->FromString('');
		$this->assertEquals($t->template_str,'');
		$this->assertEquals($t->compile_options['format_char'],null);
		$this->assertEquals($t->compile_options['meta'],null);
	}

	function testBadOptions()
	{
		$f = "Format-Char: |
Meta: <>
BAD STUFF";
		$this->setExpectedException('JsonTemplateCompilationError');
		JsonTemplateModule::pointer()->FromString($f);
	}

	function testTemplate()
	{
		$f = "format-char: :
meta: <>

Hello <there>";
		$t = JsonTemplateModule::pointer()->FromString($f);
		$this->assertEquals($t->template_str,'Hello <there>');
		$this->assertEquals($t->compile_options['format_char'],':');
		$this->assertEquals($t->compile_options['meta'],'<>');
	}

	function testNoOptions()
	{
		$f = "Hello {dude}";
		$t = JsonTemplateModule::pointer()->FromString($f);
		$this->assertEquals($t->expand(array('dude'=>'Andy')), 'Hello Andy');
	}
}


class JsonTemplateJsonTest extends PHPUnit_Framework_TestCase
{

	function testJsonData()
	{
		$t = "Hello {dude}";
		$d = array('dude'=>'Andy');
		$d = json_encode($d);
		$this->assertEquals(JsonTemplateModule::expand($t,$d),'Hello Andy');
	}

	function testJsonOptions()
	{
		$t = "Hello [[dude]]";
		$d = array('dude'=>'Andy');
		$d = json_encode($d);
		$o = array('meta'=>'[[]]');
		$o = json_encode($o);
		$this->assertEquals(JsonTemplateModule::expand($t,$d,$o),'Hello Andy');
	}

}


class JsonTemplateTemplateTest extends PHPUnit_Framework_TestCase
{
	function testNestedRepeatedSections()
	{
		$t = "
[header]
---------
[.section people]
[.repeated section @]
  [name]: [.repeated section attributes][@] [.end]
[.end][.end]";
		$d = array(
			'header'	=> 'People',
			'people'	=> array(
				array('name'=> 'Andy', 'attributes'=> array('jerk', 'cool')),
				array('name'=> 'Bob', 'attributes'=> array('nice', 'mean', 'fun')),
			),
		);
		$e = "
People
---------
  Andy: jerk cool 
  Bob: nice mean fun 
";
		$o = array('meta'=>'[]');
		$this->assertEquals(JsonTemplateModule::expand($t,$d,$o),$e);
	}


}

?>
