<?php

//// Function to get the client IP address
//function client_ip() {
//    $ipaddress = '';
//    if (isset($_SERVER['HTTP_CLIENT_IP']))
//        $ipaddress = $_SERVER['HTTP_CLIENT_IP'];
//    else if(isset($_SERVER['HTTP_X_FORWARDED_FOR']))
//        $ipaddress = $_SERVER['HTTP_X_FORWARDED_FOR'];
//    else if(isset($_SERVER['HTTP_X_FORWARDED']))
//        $ipaddress = $_SERVER['HTTP_X_FORWARDED'];
//    else if(isset($_SERVER['HTTP_FORWARDED_FOR']))
//        $ipaddress = $_SERVER['HTTP_FORWARDED_FOR'];
//    else if(isset($_SERVER['HTTP_FORWARDED']))
//        $ipaddress = $_SERVER['HTTP_FORWARDED'];
//    else if(isset($_SERVER['REMOTE_ADDR']))
//        $ipaddress = $_SERVER['REMOTE_ADDR'];
//    else
//        $ipaddress = 'UNKNOWN';
//    return $ipaddress;
//}

//$host = $_SERVER['REMOTE_HOST'];
$ip = $_SERVER['REMOTE_ADDR'];
$port = $_SERVER['REMOTE_PORT'];
$query = $_SERVER['QUERY_STRING'];
$query_uri = $_SERVER['REQUEST_URI'];
$method = $_SERVER['REQUEST_METHOD'];

$fp = fopen("serverrequestlog.txt", "a");
fwrite($fp, "IP : ".$ip."\nPORT : ".$port."\nQUERY : ".$query."\nQ_URI : ".$query_uri."\nMethod : ".$method."\n\n");
fclose($fp);
echo "lanchat3_ip>>>".$ip.":".$port."<<<"; ?>