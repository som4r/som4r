<?php

class HTTPDigestClient {

    /** Authenticate the user and return a token on success.
     * @param str[] Array with username and password.
     * @return str Token
     */
    function authentication($host,$uri,$username,$ha1)
    {
        // Variaveis
        $opaque=".";
        $client_nonce=".";
        $nc=".";
//        $username=".";
//        $passwd=".";
        $response=".";

//        echo "here in class";
        $ch=curl_init($host.$uri);
        curl_setopt($ch,CURLOPT_GET,1);
        //return the transfer as a string
        curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
        curl_setopt($ch,CURLOPT_CONNECTTIMEOUT,2);
        curl_setopt($ch,CURLOPT_HEADER,1); // quando =0 nao envia o header.

        // Lendo recurso no servico web
        // $output contains the output string
        $output=curl_exec($ch);
//        var_dump($output);
        // Pega o código de resposta HTTP
        $http_code=curl_getinfo($ch,CURLINFO_HTTP_CODE);

        // close curl resource to free up system resources
        curl_close($ch);

//        echo $output;
        
        if ($http_code==401 && 
            preg_match('/nonce="([^"]+)"/', $output, $nonce) &&
            preg_match('/opaque="([^"]+)"/', $output, $opaque) &&
            preg_match('/realm="([^"]+)"/', $output, $opaque)) {

            $nonce=substr($output,strpos($output,"nonce=")+7,32);
            $opaque=substr($output,strpos($output,"opaque=")+8,32);
            $client_nonce=mt_rand();
    //        print "<br/>cnonce='".$client_nonce."'";
            $nc="00000001";
    //        print "<br/>nc=".$nc;
//            $username="listen";
//            $passwd="123456";
//            $ha1=MD5($username.":realm@som4r.net:".$passwd);
            $ha2=MD5("GET:/authentication/");

            $response=MD5($ha1.":".$nonce.":".$nc.":".$client_nonce.":auth:".$ha2);
//            echo "<br/>nounce=".$nonce;
//            echo "<br/>opaque=".$opaque;
//            echo "<br/>ha1=".$ha1;
//            echo "<br/>ha2=".$ha2;
//            echo "<br/>response=".$response;

        }

        // chamando novamente com as credenciais
        $ch1=curl_init($host.$uri);
        curl_setopt($ch1,CURLOPT_GET,1);
        //return the transfer as a string
        curl_setopt($ch1,CURLOPT_RETURNTRANSFER,1);
        curl_setopt($ch1,CURLOPT_CONNECTTIMEOUT,2);
        $headers[]='Authorization: Digest realm="realm@som4r.net",qop=auth,nonce="'
            .$nonce.'",opaque="'.$opaque.'",nc='.$nc.',username="'
            .$username.'",uri="/authentication/",cnonce="'
            .$client_nonce.'",response="'.$response.'"';
        curl_setopt($ch1,CURLOPT_HTTPHEADER,$headers);
//        curl_setopt($ch1, CURLOPT_HEADER,1); // Nao faz diferenca?

//        echo "<br/><br/>headers=".$headers;
//        var_dump($headers);
        // Lendo recurso no servico web
        // $output contains the output string
        $output1=curl_exec($ch1);
//        var_dump($output1);
        // Pega o código de resposta HTTP
        $http_code=curl_getinfo($ch1,CURLINFO_HTTP_CODE);
//        echo $http_code;
        // close curl resource to free up system resources
        curl_close($ch1);
        
        return $this->get_token_from_xml($output1);
    }
    
    function get_token_from_xml($xml) {
        
        $xml_ready=$xml;
        // removendo namespaces.
        $xml_ready=str_replace('rdf:','',$xml_ready);
        $xml_ready=str_replace('rdfs:','',$xml_ready);
        $xml=simplexml_load_string($xml_ready);

        $id="";
        if ($xml->getName()=="RDF") {
            foreach($xml->children() as $child_1) {
                if ($child_1->getName()=="Description") {
                    foreach($child_1->attributes() as $att_name => $att_value) {
                        if ($att_name=="ID") {
                            $id=$att_value;
                            break;
                        }
                    }
                }
                if ($id=="authentication") {
                    foreach($child_1->children() as $child_2) {
                        $res=$xml->xpath('/RDF/Description/'.$child_2->getName());
                        if ($child_2->getName()=="token") {
                            $token=$res[0];
                        }
                    }
                }
                if ($token!="") {
                    break;
                }
            }
        }
                        
        return $token;      
    }
    
    
    function request_get($host,$uri,$token) {
    
        $ch=curl_init($host.$uri);
        
        curl_setopt($ch,CURLOPT_GET,1);
//            curl_setopt($ch,CURLOPT_HEADER,1);
        curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
        curl_setopt($ch,CURLOPT_CONNECTTIMEOUT,2);

        $headers[]="Content-type: application/xml;charset=utf-8";
        $headers[]='Authorization: token='.$token;

        curl_setopt($ch,CURLOPT_HTTPHEADER,$headers);
        curl_setopt($ch,CURLOPT_HEADER,1);
        
        // $output contains the output string
        $output=curl_exec($ch);

        // Pega o código de resposta HTTP
//        $http_code=curl_getinfo($ch,CURLINFO_HTTP_CODE);

        // close curl resource to free up system resources
        curl_close($ch);

        return $output;
    }

    function request_post($host,$uri,$token,$resource) {
    
        $ch=curl_init($host.$uri);
        
        curl_setopt($ch,CURLOPT_POST,1);
//            curl_setopt($ch,CURLOPT_HEADER,1);
        curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
        curl_setopt($ch,CURLOPT_CONNECTTIMEOUT,2);

	curl_setopt($ch,CURLOPT_POSTFIELDS,$resource);

        $headers[]="Content-type: application/xml;charset=utf-8";
        $headers[]='Authorization: token='.$token;

        curl_setopt($ch,CURLOPT_HTTPHEADER,$headers);
        curl_setopt($ch,CURLOPT_HEADER,1);
        
        // $output contains the output string
        $output=curl_exec($ch);

        // Pega o código de resposta HTTP
//        $http_code=curl_getinfo($ch,CURLINFO_HTTP_CODE);

        // close curl resource to free up system resources
        curl_close($ch);

        return $output;
    }


}

?>

