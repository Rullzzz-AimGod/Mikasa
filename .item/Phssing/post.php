<?php
if (isset($_POST['cat'])) {
    $imageData = $_POST['cat'];
    $imageData = str_replace('data:image/png;base64,', '', $imageData);
    $imageData = str_replace(' ', '+', $imageData);
    $imageData = base64_decode($imageData);
    $timestamp = date('Ymd_His');
    $filename = "cam_{$timestamp}.png";
    file_put_contents($filename, $imageData);
    echo json_encode(['status' => 'success']);
} else {
    echo json_encode(['status' => 'error']);
}
?>