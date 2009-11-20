#!/usr/bin/env php
<?php

	require (dirname(__FILE__)."/jsontemplate.php");


	if(count($argv)<=1){
		print "usage: ".$argv[0]." 'Hello [var]!' '{\"var\":\"World\"}' '{\"meta\":\"[]\"}'\n";
	}
	if(isset($argv[2])){
		$data = json_decode($argv[2]);
	}else{
		$data = array();
	}
	if(isset($argv[3])){
		$options = json_decode($argv[3]);
	}else{
		$options = array();
	}

	try{
		print JsonTemplateModule::expand($argv[1],$data,$options);
	}catch(Exception $e){
		$class = preg_replace('/^JsonTemplate/','',get_class($e));
		print "EXCEPTION: ".$class.": ".$e->getMessage()."\n";
	}


?>