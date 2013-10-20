<?php

    $ch = curl_init("localhost:8094/image/");
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

    return $output
?>
