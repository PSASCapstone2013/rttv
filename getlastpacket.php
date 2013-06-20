<?php

$db = new SQLite3('rocket.sqlite');
$q = $db->query('SELECT json_str FROM rocketdata WHERE idx=(SELECT MAX(idx) FROM rocketdata);');
$result = $q->fetchArray();
if(count($result) > 1) {
  echo $result[0];
}

?>