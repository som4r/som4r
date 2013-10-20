<?php

	$ip_localhost=$_SERVER['SERVER_ADDR'];
	echo $ip_localhost;
	/* Redirect browser */
//	header("Location: http://".$ip_localhost.":5080/demos/simpleSubscriber.html");
	header("Location: http://".$ip_localhost.":5080/demos/MyFlexApp.swf");
	/* Make sure that code below does not get executed when we redirect. */
	exit;
?>
