<?php

// no direct access
defined( '_JEXEC' ) or die( 'Restricted access' );

// carregado javascript
JHTML::_('behavior.tooltip');
JHTML::_('behavior.mootools');

$document = &JFactory::getDocument();
$document->addScript(JURI::base() . 'media/system/js/jquery.js');
$document->addScript(JURI::base() . 'media/system/js/jquery.timers.js');
$document->addCustomTag('<script type="text/javascript">jQuery.noConflict();</script>');

?>

<script>
    //jQuery(document.ready(alert("Hereeee");));
    jQuery(document).ready(function() { 
        //loadScript_map();
    });

    // Enviar texto.
    jQuery(function() {
        jQuery(".tts_submit").click(function() {
            // Validando texto a enviar.
            var texto = document.tts_form.elements["tts_texto"].value;
            if (texto.length > 0) {
                // envia o texto por post ao webservice tts.
                var dataString = getTtsRecursoXml(texto);
                ajax_post_wsrest_tts(dataString);
                // Atualizando a tela.
                jQuery("#tts_div").html(texto);
                jQuery("#tts_texto").val("");
            }
            jQuery("#tts_texto").focus();
        });

    });

    // Post -> tts
    function ajax_post_wsrest_tts(dataString) {
        jQuery.ajax({
                type: "POST",
                url: "<?php echo JURI::base() . 'modules/mod_tts/call_wsrest_tts.php'; ?>",
                data: dataString,
//                success: function(resultado){
//                    alert("ws post ok -> result = " + dataString + resultado);
//                }
        });

    }


    // Montando recurso em formato xml.
    function getTtsRecursoXml(texto) {
        // Montando recurso
        var recurso = "<rdf:RDF><rdf:Description rdf:ID='tts'><textToSpeech>"+texto+"</textToSpeech></rdf:Description></rdf:RDF>";
        return 'recurso=' + recurso;
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


