<?php
    include ('HTTPDigestClient.php');

    $HTTPDigestClient=new HTTPDigestClient();
    
    //echo "here";
    $token="default";

    $token=$HTTPDigestClient->authentication(
        "http://localhost:8012","/authentication/",
        "hmi_gps","0652b5f6ff93d4e6c0a99f7fad1d5aa4");
    echo $token;
    //return $token;        
?>

