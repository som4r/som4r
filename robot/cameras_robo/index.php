
<?php 
$server_ip = $_SERVER['SERVER_ADDR'];
?>

<script type="text/javascript" src="jwplayer.js"></script>

<div id="container">Loading the player ...</div>
<script type="text/javascript">

jwplayer("container").setup({
	flashplayer: "player.swf",
	allowfullscreen: "true",
	allowscriptaccess: "always",
	wmode: "transparent",
	bufferlength: 0.001,
	subscribe: "true",
	autostart: "true",
	file: "red5StreamDemo",
	streamer: "rtmp://<?php echo $server_ip; ?>/oflaDemo",
	provider: "rtmp",
	height: 360,
	width: 480
});

</script>

