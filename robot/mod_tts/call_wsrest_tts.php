<?php

    include ('HTTPDigestClient.php');

    $HTTPDigestClient=new HTTPDigestClient();

    $token=$_POST["token"];
    $recurso=$_POST["recurso"];

//    echo "token=====".$token;
//    echo "recurso===".$recurso;
    
    $token=substr($token,1,32);

    $xml_response=$HTTPDigestClient->request_post("http://localhost:8096","/",$token,$recurso);
    echo 'tts='.$xml_response;


/*
    request_get("http://localhost:8096","/",$token);

    function request_get($host,$uri,$token) {

GLOBAL $token;

	//echo "here ".$host.$uri.$token;

        $ch=curl_init($host.$uri);
        
        curl_setopt($ch,CURLOPT_GET,1);
//            curl_setopt($ch,CURLOPT_HEADER,1);
        curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
        curl_setopt($ch,CURLOPT_CONNECTTIMEOUT,2);

//        $headers[]="Content-type: application/xml;charset=utf-8";
//        $headers[]="Authorization: token={$token}";
	$headers[]="Authorization: token=".substr($token,1,32);
//	  $xy = "Authorization:token=".$token."---";
//           $headers = array($xy);
//	echo "len token = ".strlen($token)." token=".substr($token,0,32)."###";
//	print_r($headers);

        curl_setopt($ch,CURLOPT_HEADER);

        curl_setopt($ch,CURLOPT_HTTPHEADER,$headers);
//        curl_setopt($ch,CURLOPT_HEADER,1);
        
        // $output contains the output string
        $output=curl_exec($ch);

        // Pega o código de resposta HTTP
//        $http_code=curl_getinfo($ch,CURLINFO_HTTP_CODE);

        // close curl resource to free up system resources
        curl_close($ch);

        return $output;

    }
*/
?>

