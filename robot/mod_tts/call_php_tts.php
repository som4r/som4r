<?php

    $texto = $_POST["tts_texto"];
    //$texto = "1 2 3 4";
    //exec("ls / -a", $output);
    exec("espeak -vpt '".$texto."'", $output);
    //print_r($output);

    //exec("ls / -a");

?>
