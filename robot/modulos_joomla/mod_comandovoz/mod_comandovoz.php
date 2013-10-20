<?php

// no direct access
defined( '_JEXEC' ) or die( 'Restricted access' );

// Cookies. Necessário declarar pelo php para poder usar depois pelo php.
setcookie("comandovoz_velocidade", "0");
setcookie("comandovoz_direcao", "0");

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
        // Lendo estado do recurso gps.
        //ajax_call_wsrest();
        // Atualizando mapa.
        //loadScript_map();
    });

    var active = false;
    var last_id_ouvido = "0";

    // Timer
    jQuery(function() {
        jQuery(".comandovoz_div").everyTime(333,function(i) {
            //alert("teste");
            if (active == true) {
                // chama webservice do ouvido, recebe string com os dados, e atualiza os valores dos cookies.
                ajax_get_wsrest_ouvido();
                // Lendo cookies com a resposta do webservice, que foi gravada na chamada ajax acima.
                var new_id_ouvido = getCookie("ouvido_uttid");
                var new_resultado = getCookie("ouvido_resultado");
                // validar id_sequencial recebido
                // - deve ser maior o que ultimo lido/enviado, ou seja, last_id_ouvido
                // - deve ter um campo resultado nao vazio.
                // ToDo: aceitar somente comandos validos.
                // ToDo: e deve ter sido "ouvido" nos ultimos 3 segundos.
                if (new_id_ouvido != null && new_id_ouvido > last_id_ouvido
                    && new_resultado != null && new_resultado.length > 0
                    && comando_eh_valido(new_resultado) == true) {

                    // ToDo: se id for valido chama webservice do veiculo.

//                    alert("here .");
                    // Variaveis para montar o recurso.
                    dataString = getRecursoXml(new_resultado);

//                    alert("here .. " + dataString);
                    ajax_post_wsrest_veiculo(dataString);

//                    alert("here ...");
                    // grava novo id.
                    last_id_ouvido = new_id_ouvido;
                    jQuery(this).html(new_resultado);

//                    return false;
                }
            }
//          return false;
        });
    });

    // Ativar/desativar comando de voz.
    jQuery(function() {
        jQuery(".comandovoz_submit").click(function() {
            // Lendo estado do checkbox.
            if (document.comandovoz_form.elements["comandovoz_checkbox"].checked == true) {
                // le e armazena id_sequencial do webservice ouvido.
                ajax_get_wsrest_ouvido();
                // Lendo cookies com a resposta do webservice, que foi gravada na chamada ajax acima.
                last_id_ouvido = getCookie("ouvido_uttid");
                if (last_id_ouvido == null) { last_id_ouvido = "0"; }
                active = true;
            } else
                active = false;
        });

    });

    // Post -> veiculo
    function ajax_post_wsrest_veiculo(dataString) {
        jQuery.ajax({
                type: "POST",
                url: "<?php echo JURI::base() . 'modules/mod_comandovoz/call_wsrest_veiculo.php'; ?>",
                data: dataString,
//                success: function(resultado){
//                    alert("ws post ok -> result = " + dataString + resultado);
//                }
        });

    }

    // get <- ouvido
    function ajax_get_wsrest_ouvido() {
        //alert("ajax_get: " + "<?php echo JURI::base() . 'modules/mod_comandovoz/call_wsrest_ouvido.php'; ?>");
        jQuery.get("<?php echo JURI::base() . 'modules/mod_comandovoz/call_wsrest_ouvido.php'; ?>",
            function(data) {
                //alert("Data Loaded: " + data);
                // Gravando cookies com os dados retornados pelo servico web.
                string_to_cookies(data);
            }
        );
    }

    function string_to_cookies(stringData) {
        var lista = stringData.split(",");
//        alert("length = " + lista.length);
        if (lista[0] == "OuvidoRO") {
            for (var i = 1; i < (lista.length - 1); i++) {
                // Separando chave:valor
                var cookieData = lista[i].split(":");
                // Armazenando nos cookies
                setCookie("ouvido_" + cookieData[0], cookieData[1]);
            }
        }
    }
    
    function comando_eh_valido(comando_resultado) {
        // ToDo: - validar comandos
        if (comando_resultado.length > 0)
            return true;
            // ToDo: se comando eh valido retorna o comando e velocidade? para enviar ao wsrest_veiculo.
        else
            return false;
    }

    // Montando recurso em formato xml a partir dos cookies.
    function getRecursoXml(new_resultado) {
        var velocidade = getCookie("comandovoz_velocidade");
        if (velocidade == null) {
            velocidade = "0";
        }
        var direcao = getCookie("comandovoz_direcao");
        if (direcao == null) {
            direcao = "5";
        }
//        alert("velocidade e direcao   " + velocidade + "  " + direcao);
        // Direcao e/ou velocidade
        if (new_resultado == "STOP")
            direcao = "5";
        else if (new_resultado == "AHEAD")
            direcao = "2";
        else if (new_resultado == "BACK")
            direcao = "8";
        else if (new_resultado == "RIGHT")
            direcao = "6";
        else if (new_resultado == "LEFT")
            direcao = "4";
        else if (new_resultado == "AHEAD RIGHT")
            direcao = "3";
        else if (new_resultado == "AHEAD LEFT")
            direcao = "1";
        else if (new_resultado == "FAST")
            velocidade = "100";
        else if (new_resultado == "SLOW")
            velocidade = "80";
        // Velocidade
        // ToDo: Tornar os percentuais configuraveis no modulo do Joomla.

        // Se parar entao velocidade zero.
        if (parseInt(direcao) == 5 || parseInt(direcao) == 0) {
            velocidade = "0";
        }
        // Senao se velocidade zero entao velocidade baixa.
        else if (parseInt(velocidade) == 0) {
            velocidade = "80";
        }

        // Armazenando nos cookies
        setCookie("comandovoz_velocidade", velocidade);
        setCookie("comandovoz_direcao", direcao);

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
    
</script>

<form name="comandovoz_form">
    <input id="comandovoz_checkbox" type="checkbox" class="comandovoz_submit" /> Ativado.
    <br /><br/>
    Ultimo comando:
    <div class="comandovoz_div">...</div>
</form>

