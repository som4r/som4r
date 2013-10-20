<?php

    //$teste = $_POST["teste"];

    $ch = curl_init("localhost:8090"); //  localhost/wsrest_audicao
    curl_setopt($ch, CURLOPT_GET, 1);
    //return the transfer as a string
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 2);

    // Lendo recurso no servico web
    // $output contains the output string
    $output = curl_exec($ch);
//    echo "xml from localhost:8080 ";
//    var_dump($output);

    // Pega o código de resposta HTTP
    //	$resposta = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    // close curl resource to free up system resources
    curl_close($ch);

    // lendo xml recebido do servico web e gravando os dados em formato ?json?.
    $output_json = "";
    $xml = simplexml_load_string($output);
    if ($xml->getName() == "OuvidoRO") {
        $output_json .= $xml->getName() . ",";
        foreach($xml->children() as $child) {
            $output_json .= $child->getName() . ":" . $child . ",";
        }
    }

    echo $output_json;
//    return $output;

?>