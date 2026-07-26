<?php
$count = isset($_GET['count']) ? $_GET['count'] : 0;
file_put_contents('notify.log', $count . "\n", FILE_APPEND);
?>