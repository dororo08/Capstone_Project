<?php
$jb_conn = mysqli_connect('localhost', 'root', 'rlaehgus6169*', 'test');

$jb_sql_select = "SELECT carnumber, phonenumber, violate, fee FROM car;";
$jb_result = mysqli_query($jb_conn, $jb_sql_select);
?>

<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>당일 주차차량 조회</title>
  <style>
    body {
      font-family: Consolas, monospace;
      font-size: 12px;
    }

    table {
      width: 100%;
    }

    th, td {
      padding: 10px;
      border-bottom: 1px solid #dadada;
    }
  </style>
</head>
<body>
<h2>당일 주차차량 조회</h2>
<table>
  <thead>
  <tr>
    <th>차량 번호</th>
    <th>전화 번호</th>
    <th>위반 횟수</th>
    <th>과태료</th>
  </tr>
  </thead>
  <tbody>
  <?php
  while ($jb_row = mysqli_fetch_array($jb_result)) {
    echo '<tr>';
    echo '<td>' . $jb_row['carnumber'] . '</td>';
    echo '<td>' . $jb_row['phonenumber'] . '</td>';
    echo '<td>' . $jb_row['violate'] . '</td>';
    echo '<td>' . $jb_row['fee'] . '</td>';
    echo '</tr>';
  }
  ?>
  </tbody>
</table>
<button onclick="location.href='2.php'">홈으로</button>
</body>
</html>