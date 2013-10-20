<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
 "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8">
<title>Canvas 3D</title>

<link type="text/css" rel="stylesheet" href="canvas3dcsstest.css" media="screen">

<?php
// Cookies. Necessário declarar pelo php para poder usar depois pelo php.
setcookie("depth_chart_tilt_angle", "0");
?>

<script type="text/javascript" src="jquery.js"></script>
<script type="text/javascript" src="canvas3DGraph.js"></script>
<script type="text/javascript" src="jquery.timers.js"></script>
<script type="text/javascript" src="cookies.js"></script>

<script type="text/javascript">

$(document).ready(function() {

	ajax_call_wsrest_kinect();



// Timer
$(function() {
	$(".robot_depth_chart").everyTime(250,function(i) {
//		alert("here minuto");
		ajax_call_wsrest_kinect();
	});

});

$(function() {
	$(".depth_chart_submit").click(function() {
//alert("here submit");
		    var valor = $(this).val();
		    dataString = getRecursoXml(valor);
//	            alert ('datastring 2 tilt - xml = ' + dataString);
		    ajax_call_wsrest_kinect_tilt(dataString);

		    return false;
	});
});

//$(document).ready(alert("Hereeee"));

function refresh_kinect_depth(stringData) {
//alert("here");

        //Initialise Graph  
        var g = new canvasGraph('graph');  
                  
        //define some data  
        gData=new Array();  
                  
	var lista = stringData.split(",");
//	        alert("length = " + lista.length);
//	        alert("lista[0] = " + lista[0]);
	if (lista[0] == "KinectDepth2D") {
		for (var i = 1; i < (lista.length - 1); i+=5) {
			// Separando chave:valor
			var key_value = lista[i].split(":");
			// plotando dados.
			// Ajustando escala 
			// (limiar minimo = 380 = +-0.45m, maximo = 955 = +-2.5m)
			//var leitura = 575-(parseInt(key_value[1])-380);

			//var leitura = 575-(parseInt(key_value[1])*575/1024);//    l/1024 = x/575

			// entre 45 e 350cm  // l/350 = x/575
			var leitura = parseInt((0.1236 * Math.tan(parseInt(key_value[1])/2842.5 + 1.1863))*100);
			leitura = 575 - (leitura*575/350)
			if (leitura < 0) {
				leitura = 0;
			}
		        gData[parseInt(key_value[0].substring(1))]={x:parseInt(key_value[0].substring(1)),y:540,z:leitura};  
		}
	}

        // sort data - draw farest elements first         
        gData.sort(sortNumByZ);  
                  
        //draw graph   
        g.drawGraph(gData); 

}

// Get <- kinect/depth
function ajax_call_wsrest_kinect() {
//alert("Here");
	$.get('call_wsrest_kinect_depth.php',
		function(data) {
//alert("Data Loaded::: " + data);
			// Atualizando o grafico com os dados retornados pelo servico web.
			refresh_kinect_depth(data);
		}
	);
}


// Post -> kinect/tilt
function ajax_call_wsrest_kinect_tilt(dataString) {
//	alert("call tilt");
        $.ajax({
                type: "POST",
                url: "call_wsrest_kinect_tilt.php",
                data: dataString,
//                success: function(resultado){
//                    alert("ws post ok -> result = " + dataString + resultado);
//                }
        });

}

// Montando recurso em formato xml a partir dos cookies.
function getRecursoXml(valor) {
        var depth_chart_tilt_angle = getCookie("depth_chart_tilt_angle");
        if (depth_chart_tilt_angle == null) {
            depth_chart_tilt_angle = "0";
        }
        // depth_chart_tilt_angle
        // ToDo: Tornar o incremento configuravel no modulo do Joomla.
	if (valor == "1" || valor == "2" || valor == "3") {
            if (valor == "1") {
		depth_chart_tilt_angle = "" + Math.min(parseInt(depth_chart_tilt_angle) + 5, 25);
            }
            if (valor == "2") {
                depth_chart_tilt_angle = "0";
            }
            if (valor == "3") {
                depth_chart_tilt_angle = "" + Math.max(parseInt(depth_chart_tilt_angle) - 5, -25);
            }
        }
        // Armazenando nos cookies
        setCookie("depth_chart_tilt_angle", depth_chart_tilt_angle);

        // Atualizando a tela.
        jQuery("#depth_chart_tilt_angle_atual").val(depth_chart_tilt_angle);

        // Id timeout
        var id = "" + new Date().getTime();

        // Montando recurso
        var recurso = "<KinectTiltLed>"
            + "<tilt>" + depth_chart_tilt_angle + "</tilt>"
            + "<id>" + id + "</id>"
            + "</KinectTiltLed>";
        return 'recurso=' + recurso;
}
 
});

</script>
</head>
<body>


<div style="clear: both;"></div>
<div style="float:left;" onmousedown="return false">
    <input type="image" value="1" class="depth_chart_submit" src="./images/up.png" alt="Acima" />
</div>
<div style="float:left;" onmousedown="return false">
    <input type="image" value="2" class="depth_chart_submit" src="./images/center.png" alt="Centro" />
</div>
<div style="float:left;" onmousedown="return false">
    <input type="image" value="3" class="depth_chart_submit" src="./images/down.png" alt="Abaixo" />
</div>
<div style='float:left;'><p><b>
    Tilt:
    <input type="text" id="depth_chart_tilt_angle_atual" 
        value="<?php echo $_COOKIE["depth_chart_tilt_angle"]; ?>" disabled="true" size="2" />
    </b></p>
</div>
<div style="clear: both;"></div>

<div id="g-holder">  
    <div id="canvasDiv">  
        <canvas id="graph" width="300" height="300" class="robot_depth_chart"></canvas>  
        <div id="gInfo"></div>   
    </div>  
    <div id="controls">  
    <!-- (put your controls here, if you need any) -->  
    </div>  
</div>


</body>
</html>
