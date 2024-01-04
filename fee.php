<?php
$jb_conn = mysqli_connect('localhost', 'root', 'rlaehgus6169*', 'test');

$jb_sql_select = "SELECT idfee, feemoney, date FROM fee";
$jb_result = mysqli_query($jb_conn, $jb_sql_select);
?>

<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>신고완료 차량 조회</title>
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

<table>
  <thead>
  <tr>
    <th>차량번호</th>
    <th>과태료</th>
    <th>날짜</th>
  </tr>
  </thead>
  <tbody>
  <?php
  while ($jb_row = mysqli_fetch_array($jb_result)) {
    echo '<tr>';
    echo '<td>' . $jb_row['idfee'] . '</td>';
    echo '<td>' . $jb_row['feemoney'] . '</td>';
    echo '<td>' . $jb_row['date'] . '</td>';
    echo '</tr>';
  }
  ?>
  </tbody>
</table>
<button onclick="location.href='2.php'">홈으로</button>
</body>
</html>