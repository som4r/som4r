<?php

// no direct access
defined( '_JEXEC' ) or die( 'Restricted access' );

// Cookies. Necessário declarar pelo php para poder usar depois pelo php.
setcookie("mod_tts_token", "default");

// carregado javascript
JHTML::_('behavior.tooltip');
JHTML::_('behavior.mootools');

$document = &JFactory::getDocument();
$document->addScript(JURI::base() . 'media/system/js/xml_util.js');
$document->addScript(JURI::base() . 'media/system/js/jquery.js');
$document->addScript(JURI::base() . 'media/system/js/jquery.timers.js');
$document->addCustomTag('<script type="text/javascript">jQuery.noConflict();</script>');

?>

<script>
    //jQuery(document.ready(alert("Hereeee");));
    jQuery(document).ready(function() {

	// Autenticacao.
        ajax_get_authentication();
//	var token=getCookie("mod_tts_token");
//	alert("token0="+token);
    });

    // Enviar texto.
    jQuery(function() {
        jQuery(".tts_submit").click(function() {
            // Validando texto a enviar.
            var texto = document.tts_form.elements["tts_texto"].value;
            if (texto.length > 0) {                
                // envia o texto por post ao webservice tts.
                var resource_array=new Array();
                resource_array.push("text_to_speech:"+texto);
                var resource_rdfxml=array_to_rdfxml(resource_array,"tts");
//                alert("rdfxml="+resource_rdfxml);
//                var dataString=getTtsRecursoXml(resource_array);
//		var token=getCookie("mod_tts_token");
//		dataString="token="+token+"&"+dataString;
//		alert("datastring = "+dataString);
                ajax_post_wsrest_tts(resource_rdfxml);
                // Atualizando a tela.
                jQuery("#tts_div").html(texto);
                jQuery("#tts_texto").val("");
            }
            jQuery("#tts_texto").focus();
        });

    });


    function ajax_get_authentication() {
        jQuery.get("<?php echo JURI::base() . 'modules/mod_tts/call_authentication.php'; ?>",
            function(data) {
                // Gravando cookies com os dados retornados pelo servico web.
                setCookie("mod_tts_token",data);
            }
        );
    }

    // Post -> tts
    function ajax_post_wsrest_tts(dataString) {
	var token=getCookie("mod_tts_token");
//	alert("token="+token+" len ="+token.length);
	jQuery.post("<?php echo JURI::base() . 'modules/mod_tts/call_wsrest_tts.php'; ?>",
		{"token":token,"recurso":dataString},
		function(response){
		      // success code goes here
//		      alert("resultado do post="+response);
		}
	);
    }


</script>

<form name="tts_form" >
    Text to Speech
    <br />
    <textarea id="tts_texto" name="tts_texto" cols="20" rows="3"></textarea>
    <input type="button" value="Enviar" class="tts_submit" />
    <br />
    Ultimo tts:
    <div id="tts_div">...</div>
</form>


