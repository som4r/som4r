<?php

    $teste = $_POST["teste"];

    $ch = curl_init("localhost:8094/depth/");
    curl_setopt($ch, CURLOPT_GET, 1);
    //return the transfer as a string
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 2);

    // Lendo recurso no servico web
    // $output contains the output string
    $output = curl_exec($ch);

    // Pega o código de resposta HTTP
    //	$resposta = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    // close curl resource to free up system resources
    curl_close($ch);

    // lendo xml recebido do servico web e gravando os dados em formato ?json?.
    $output_json = "";
    $xml = simplexml_load_string($output);
    if ($xml->getName() == "KinectDepth2D") {
        $output_json .= $xml->getName() . ",";
        foreach($xml->children() as $child) {
            $output_json .= $child->getName() . ":" . $child . ",";
        }
    }

//echo exec('whoami');

    echo $output_json;
//    return $output_json;

?>
