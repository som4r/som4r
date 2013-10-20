<?php

    $recurso = $_POST["recurso"];

    $ch = curl_init("localhost:8080/");
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 2);

    curl_setopt($ch, CURLOPT_POSTFIELDS, $recurso);

    $output = curl_exec($ch);
    // Pega o código de resposta HTTP
    //	$resposta = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    curl_close($ch);
    return $output;

?>
