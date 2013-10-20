<?php

    header("Content-type: text/plain");

    $ch = curl_init("localhost:8092/");
    curl_setopt($ch, CURLOPT_GET, 1);
    //return the transfer as a string
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 2);

    // Lendo recurso no servico web
    // $output contains the output string
    $output = curl_exec($ch);
#    echo "xml from localhost:8080 ";
#    var_dump($output);

    // Pega o código de resposta HTTP
    //	$resposta = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    // close curl resource to free up system resources
    curl_close($ch);

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
//    return $output;

?>
