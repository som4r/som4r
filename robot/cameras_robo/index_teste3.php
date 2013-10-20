
<?php 
$streamurl = 'rtmp://'.$_SERVER['SERVER_ADDR'].':1935/oflaDemo'; 
$server_ip = $_SERVER['SERVER_ADDR'];
echo $streamurl;
?>

<script type="text/javascript" src="jwplayer.js"></script>

<div id="container">Loading the player ...</div>
<script type="text/javascript">
jwplayer("container").setup({
flashplayer: "player.swf",
type: "rtmp",
allowfullscreen: "false",
allowscriptaccess: "always",
wmode: "transparent",
bufferlength: 0,
subscribe: "true",
autostart: "true",
file: "rtmp://localhost:1935/oflaDemo",
streamer: "rtmp://localhost:1935/",
height: 360,
width: 480
});
</script>

