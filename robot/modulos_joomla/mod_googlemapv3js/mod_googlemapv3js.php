<?php

// no direct access
defined( '_JEXEC' ) or die( 'Restricted access' );

// carregado javascript
JHTML::_('behavior.tooltip');
JHTML::_('behavior.mootools');

$document = &JFactory::getDocument();
$document->addScript(JURI::base() . 'media/system/js/jquery.js');
$document->addCustomTag('<script type="text/javascript">jQuery.noConflict();</script>');

$document->addScript(JURI::base() . 'media/system/js/cookies.js');

$document->addCustomTag('<meta name="viewport" content="initial-scale=1.0, user-scalable=yes" />');
$document->addCustomTag('<style type="text/css">
  html { height: 200px }
  body { height: 200px; margin: 0px; padding: 0px }
  #map_canvas { height: 200px }
</style>');
//$document->addScript('http://maps.google.com/maps/api/js?sensor=false');

?>


<script>

    // Nome das funcoes declaradas em cada modulo deve ser unico.
    // ==========================================================

    //jQuery(document.ready(alert("Hereeee");));
    jQuery(document).ready(function() { 
        
        // Lendo estado do recurso gps.
        gps_ajax_call_wsrest();
        // Atualizando mapa.
        gps_loadScript_map();

    });


    var map;
    var zoom = 8;

    function gps_initialize_map() {

        // Lendo cookies com a resposta do gps, que foi gravada na chamada ajax (acima).
        var latitude = getCookie("gps_latitude");
        if (latitude == null) { latitude = "0"; }
        var longitude = getCookie("gps_longitude");
        if (longitude == null) { longitude = "0"; }
        var altitude = getCookie("gps_altitude");
        if (altitude == null) { altitude = "0"; }
        var angulo = getCookie("gps_angulo");
        if (angulo == null) { angulo = "0"; }
        var gps_id = getCookie("gps_id");
        if (gps_id == null) { gps_id = "0"; }
        
        var posicao = latitude + " : " + longitude;
        //setCookie("gps_latitude", valor);
        // Atualizando a tela.
        jQuery("#gps_posicao_atual").val(posicao);

        var latlng = new google.maps.LatLng(parseFloat(latitude), parseFloat(longitude));
        var myOptions = {
            zoom: zoom,
            center: latlng,
            scaleControl: true,
            mapTypeId: google.maps.MapTypeId.HYBRID
        };
        map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

        google.maps.event.addListener(map, 'zoom_changed', function() {
            zoom = map.getZoom();
        });

        var marker = new google.maps.Marker({
            position: latlng,
            map: map,
            title:"Robô!"
        });
    }

    function gps_loadScript_map() {
        var script = document.createElement("script");
        script.type = "text/javascript";
        script.src = "http://maps.google.com/maps/api/js?sensor=false&callback=gps_initialize_map";
        document.body.appendChild(script);
    }

    function gps_ajax_call_wsrest() {
        jQuery.get("<?php echo JURI::base() . 'modules/mod_googlemapv3js/call_wsrest_gps.php'; ?>",
            function(data) {
//                alert("Data Loaded: " + data);
                // Gravando cookies com os dados retornados pelo servico web.
                gps_string_to_cookies(data);
            }
        );
    }
    
    function gps_string_to_cookies(stringData) {
//        alert("Here string_to_cookies");
        var lista = stringData.split(",");
//        alert("length = " + lista.length);
//        alert("lista[0] = " + lista[0]);
        if (lista[0] == "gps") {
            for (var i = 1; i < (lista.length - 1); i++) {
                // Separando chave:valor
                var cookieData = lista[i].split(":");
		//if cookieData.length==2 {
	                // Armazenando nos cookies
		        setCookie("gps_" + cookieData[0], cookieData[1]);
		//} else alert("detail length zero " + cookieData[0]);
            }
        }
    }

    jQuery(function() {
        jQuery(".gps_submit").click(function() {
            // Lendo estado do recurso gps.
            gps_ajax_call_wsrest();
            // Atualizando mapa.
            gps_loadScript_map();

            return false;
        });

    });

</script>

<?php
    $path_image = JURI::base() . 'modules/mod_googlemapv3js/imagens/';
?>

<div onmousedown="return false">
Pos:
<input type="text" id="gps_posicao_atual" disabled="true" size="10" />

    <span class="hasTip" title="<?php echo JText::_('Atualizar'); ?>">
        <input type="image" src="<?php echo $path_image . 'refresh.png' ?>"
               alt="" class="gps_submit"/>
        <!-- id="refresh" onclick="loadScript_map();" -->
               
    </span>
</div>

<div id="map_canvas" style="width:200px; height:200px"></div>

