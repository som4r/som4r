
<div id="flashContain">

<?php 
$streamurl = 'rtmp://'.$_SERVER['SERVER_ADDR'].':1935/oflaDemo'; 
$server_ip = $_SERVER['SERVER_ADDR'];
echo $streamurl;
?>

<script type='text/javascript' src='swfobject.js'></script>
<script type="text/javascript" src="jwplayer.js"></script>


<script type='text/javascript'>
var s1 = new SWFObject('player.swf','player','640','480','9');
s1.addVariable('allowfullscreen','false');
s1.addVariable('allowscriptaccess','always');
s1.addVariable("wmode", "transparent");
s1.addVariable("type", "rtmp");
s1.addVariable("bufferlength", "0");
s1.addVariable("subscribe", "true");
s1.addVariable("autostart", "true");
s1.addVariable('file','<?php print $streamurl; ?>');
s1.write('flashContain');
</script>

</div><!-- End "flashContain" DIV -->

