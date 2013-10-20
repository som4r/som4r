
<?php 
$streamurl = 'rtmp://'.$_SERVER['SERVER_ADDR'].':1935/oflaDemo'; 
$server_ip = $_SERVER['SERVER_ADDR'];
echo $streamurl;
?>

<script type="text/javascript" src="swfobject.js"></script>
<script type="text/javascript" src="jwplayer.js"></script>

<div id='container'>The player will be placed here</div>

<script type="text/javascript">
//  var flashvars = {
//    file:'oflaDemo',
//    streamer:'rtmp://localhost:1935/'
//  };

var flashvars = {
'type':'rtmp',
'file':'oflaDemo',
'streamer':'rtmp//192.168.1.104/',
'provider':'rtmp ',
'autostart':'true'
};

  swfobject.embedSWF('player.swf','container','480','270','9.0.115','false', flashvars,

   {allowfullscreen:'true',allowscriptaccess:'always'},
   {id:'jwplayer',name:'jwplayer'}

  );
</script>
