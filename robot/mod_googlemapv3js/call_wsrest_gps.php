<?php

    header("Content-type: text/plain");
    
    include ('HTTPDigestClient.php');

    $HTTPDigestClient=new HTTPDigestClient();

    $token=$_POST["token"];
    
    if (strlen($token)>32) {
        $token=substr($token,1,32); }

    $output=$HTTPDigestClient->request_get("http://localhost:8092","/",$token);

    // removendo namespaces.
    $xml_ready=str_replace('rdf:','',$output);
    $xml_ready=str_replace('rdfs:','',$xml_ready);
    $xml=simplexml_load_string($xml_ready);

    // lendo xml recebido do servico web e gravando os dados em formato ?json?.
    $output_json="";
    $rdf_gps=0;
    if ($xml->getName() == "RDF") {
	foreach($xml->children() as $child_1) {
		if ($child_1->getName()=="Description") {
			foreach($child_1->attributes() as $att_name => $att_value) {
				if ($att_name=="ID" and $att_value=="gps") {
					$rdf_gps=1;
					$output_json.="gps,";
					break;
				}
			}
			if ($rdf_gps==1) {
				foreach($child_1->children() as $child_2) {
					$res=$xml->xpath('/RDF/Description/'.$child_2->getName());
					$output_json.=$child_2->getName().":".$res[0].",";
				}
			}
		}
	}
    }

    echo $output_json;

?>
