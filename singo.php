<?php

include_once("connect.php");


$idfee = $_POST["idfee"];
$feemoney = $_POST["feemoney"];
$date = $_POST["date"];

echo "<h3>차량번호는 {$idfee}, 과태료는 {$feemoney}, 신고 날짜는 $date</h3>";


$sql = "INSERT INTO fee (idfee, feemoney, date) VALUES ('$idfee', '$feemoney', '$date')";
if($conn->query($sql))echo "<h3>신고등록 성공</h3>";
else echo "<h3>신고등록 실패</h3>";

?>
<html>
<button onclick="location.href='2.php'">홈으로</button>
</html>