<?php
    include ('HTTPDigestClient.php');

    $HTTPDigestClient=new HTTPDigestClient();
    
    //echo "here";
    $token="default";

    $token=$HTTPDigestClient->authentication(
        "http://localhost:8012","/authentication/",
        "hmi_tts","35e72480c15c9f5ea71fad5b75788712");
    echo $token;
    //return $token;        
?>

