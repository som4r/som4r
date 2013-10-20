<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
 "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8">
<title>Image Depth test</title>

<?php
// Cookies. Necessário declarar pelo php para poder usar depois pelo php.
setcookie("depth_chart_tilt_angle", "0");
?>

<script type="text/javascript" src="jquery.js"></script>
<script type="text/javascript" src="jquery.timers.js"></script>
<script type="text/javascript" src="cookies.js"></script>
<script type="text/javascript" src="jcanvas.min.js"></script>

<script type="text/javascript">

$(document).ready(function() {

	//ajax_call_wsrest_kinect();



// Timer
$(function() {
	$(".robot_depth_chart").everyTime(300,function(i) {
//		alert("here minuto");
//		ajax_call_wsrest_kinect_depth_image();
		var timestamp = new Date().getTime();
//		$("#holder").html("<img src='http://localhost:8094/image/"+timestamp +"' alt='' width='300' height='300' />");
//		$("#holder").show();
//		$('#holder').load('http://localhost:8094/image/');
//$("#mensagem").empty().html(retorno);
//$("#conteudo").show();

//		$(this).clearCanvas();

		
		$('canvas').drawImage({
		  source: "http://localhost:8094/image/"+timestamp,
		  x: 0, y: 0,
		  width: 300,
		  height: 300,
		  fromCenter: false
		});
//		alert("here minuto");
	});

});


//$(document).ready(alert("Hereeee"));

// Get <- kinect/depth
function ajax_call_wsrest_kinect_depth_image() {
//alert("Here");
	$.get('call_wsrest_kinect_depth_image.php',
		function(data) {
//alert("Data Loaded::: " + data);
			// Atualizando o grafico com os dados retornados pelo servico web.
//			$("#holder").empty().html(data);
		$('canvas').clearCanvas().drawImage({
		  source: data,
		  x: 0, y: 0,
		  width: 300,
		  height: 300,
		  fromCenter: false
		});
		}
	);
}


 
});

</script>
</head>
<body>

<div style="clear: both;"></div>
<!--
<div id="holder" class="robot_depth_chart">
<img src='http://localhost:8094/image/' alt='' width='300' height='300' />
</div>
-->

<canvas class="robot_depth_chart" width="300" height="300"></canvas>


</body>
</html>
