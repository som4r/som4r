<?php

// no direct access
defined( '_JEXEC' ) or die( 'Restricted access' );

// Sessao
//$session = JFactory::getSession();
//$session->set("veiculo_velocidade","0");
//$mymessage = $session->get('veiculo_velocidade');

// Cookies. Necessário declarar pelo php para poder usar depois pelo php.
setcookie("veiculo_velocidade", "0");
setcookie("veiculo_direcao", "0");

// carregado javascript
JHTML::_('behavior.tooltip');
JHTML::_('behavior.mootools');

$document = &JFactory::getDocument();
$document->addScript(JURI::base() . 'media/system/js/jquery.js');
$document->addCustomTag( '<script type="text/javascript">jQuery.noConflict();</script>' );
//$document->addScript(JURI::base() . 'modules/mod_veiculo/veiculo.js');

//if($_POST){
//	echo $_POST["botao"];
//}

?>

<script>

// TODO: ver como capturar teclado com jquery (plugin).

jQuery(document).ready(function() {

    jQuery(function() {
        jQuery(".veiculo_submit").click(function() {

            var valor = jQuery(this).val();
            dataString = getRecursoXml(valor);

//            alert ('datastring xml = ' + dataString);
            ajax_call_wsrest(dataString);

            return false;
        });

    });

    function ajax_call_wsrest(dataString) {
        jQuery.ajax({
                type: "POST",
                url: "<?php echo JURI::base() . 'modules/mod_veiculo/call_wsrest_veiculo.php'; ?>",
                data: dataString,
//                success: function(resultado){
//                    alert("ws post ok -> result = " + dataString + resultado);
//                }
        });

    }

    // Montando recurso em formato xml a partir dos cookies.
    function getRecursoXml(valor) {
        var velocidade = getCookie("veiculo_velocidade");
        if (velocidade == null) {
            velocidade = "0";
        }
        var direcao = getCookie("veiculo_direcao");
        if (direcao == null) {
            direcao = "5";
        }
        // Velocidade
        // ToDo: Tornar os percentuais configuraveis no modulo do Joomla.
	if (valor == "VB" || valor == "VM" || valor == "VA") {
            if (valor == "VA") {
                velocidade = "100";
            }
            if (valor == "VM") {
                velocidade = "90";
            }
            if (valor == "VB") {
                velocidade = "80";
            }
        }
        // Direcao
        var teste = parseInt(valor);
        if (teste >= 1 && teste <= 9) {
            direcao = valor;
        }
        // Se parar entao velocidade zero.
        if (parseInt(direcao) == 5 || parseInt(direcao) == 0) {
            velocidade = "0";
        }
        // Senao se velocidade zero entao velocidade baixa.
        else if (parseInt(velocidade) == 0) {
            velocidade = "80";
        }

        // Armazenando nos cookies
        setCookie("veiculo_velocidade", velocidade);
        setCookie("veiculo_direcao", direcao);

        // Atualizando a tela.
        jQuery("#veiculo_direcao_atual").val(direcao);
        jQuery("#veiculo_velocidade_atual").val(velocidade);

        // Id timeout
        var id = "" + new Date().getTime();

        // Montando recurso
        var recurso = "<VeiculoRO>"
            + "<direcao>" + direcao + "</direcao>"
            + "<velocidade>" + velocidade + "</velocidade>"
            + "<id_timeout>" + id + "</id_timeout>"
            + "</VeiculoRO>";
        return 'recurso=' + recurso;
    }

//    function setCookie(name, value) {
//        var curCookie = name + "=" + escape(value);
//        document.cookie = curCookie;
//    }
//
//    /*
//      name - name of the desired cookie
//      return string containing value of specified cookie or null
//      if cookie does not exist
//    */
//    function getCookie(name) {
//        var dc = document.cookie;
//        var prefix = name + "=";
//        var begin = dc.indexOf("; " + prefix);
//        if (begin == -1) {
//            begin = dc.indexOf(prefix);
//            if (begin != 0) return null;
//        } else
//            begin += 2;
//        var end = document.cookie.indexOf(";", begin);
//        if (end == -1)
//            end = dc.length;
//        return unescape(dc.substring(begin + prefix.length, end));
//    }

});

</script>


<?php
    $path_image = JURI::base() . 'modules/mod_veiculo/imagens/';
?>

<div style='float:left;'><p><b>
    <?php echo JText::_("Direcão"); ?>:
    <input type="text" id="veiculo_direcao_atual" 
        value="<?php echo $_COOKIE["veiculo_direcao"]; ?>" disabled="true" size="2" />
    </b></p>
</div>

<div style="clear: both;"></div>
<div style="float:left;" onmousedown="return false">
<!--    <input type="submit" value="1" class="veiculo_submit" /> -->
    <input type="image" value="1" class="veiculo_submit" src="<?php echo $path_image . '1.png' ?>" alt="" />
</div>
<div style="float:left;" onmousedown="return false">
    <input type="image" value="2" class="veiculo_submit" src="<?php echo $path_image . '2.png' ?>" alt="" />
</div>
<div style="float:left;" onmousedown="return false">
    <input type="image" value="3" class="veiculo_submit" src="<?php echo $path_image . '3.png' ?>" alt="" />
</div>
<div style="clear: both;"></div>
<div style="float:left;" onmousedown="return false">
    <input type="image" value="4" class="veiculo_submit" src="<?php echo $path_image . '4.png' ?>" alt="" />
</div>
<div style="float:left;" onmousedown="return false">
    <span class="hasTip" title="<?php echo JText::_('Parar'); ?>">
    <input type="image" value="5" class="veiculo_submit" src="<?php echo $path_image . '5.png' ?>" alt="" />
    </span> 
</div>
<div style="float:left;" onmousedown="return false">
    <input type="image" value="6" class="veiculo_submit" src="<?php echo $path_image . '6.png' ?>" alt="" />
</div>
<div style="clear: both;"></div>
<div style="float:left;" onmousedown="return false">
    <input type="image" value="7" class="veiculo_submit" src="<?php echo $path_image . '7.png' ?>" alt="" />
</div>
<div style="float:left;" onmousedown="return false">
    <input type="image" value="8" class="veiculo_submit" src="<?php echo $path_image . '8.png' ?>" alt="" />
</div>
<div style="float:left;" onmousedown="return false">
    <input type="image" value="9" class="veiculo_submit" src="<?php echo $path_image . '9.png' ?>" alt="" />
</div>
<div style="clear: both;"></div>
<br />

<div style='float:left;'><p><b>
    <?php echo JText::_("Velocidade"); ?>:
    <input type="text" id="veiculo_velocidade_atual" 
        value="<?php echo $_COOKIE["veiculo_velocidade"]; ?>" disabled="true" size="2" />
    </b></p>
</div>

<div style="clear: both;"></div>
<div style="float:left;" onmousedown="return false">
    <span class="hasTip" title="<?php echo JText::_('Baixa'); ?>">
    <input type="image" value="VB" class="veiculo_submit" src="<?php echo $path_image . 'v1.png' ?>" alt="" />
    </span>
</div>
<div style="float:left;" onmousedown="return false">
    <span class="hasTip" title="<?php echo JText::_('Média'); ?>">
    <input type="image" value="VM" class="veiculo_submit" src="<?php echo $path_image . 'v2.png' ?>" alt="" />
    </span>
</div>
<div style="float:left;" onmousedown="return false">
    <span class="hasTip" title="<?php echo JText::_('Alta'); ?>">
    <input type="image" value="VA" class="veiculo_submit" src="<?php echo $path_image . 'v3.png' ?>" alt="" />
    </span>
</div>
<br />
