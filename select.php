<?php
$jb_conn = mysqli_connect('localhost', 'root', 'rlaehgus6169*', 'test');

$jb_sql_select = "SELECT carnumber, phonenumber, violate, fee FROM car WHERE prove = 1 LIMIT 8;";
$jb_result = mysqli_query($jb_conn, $jb_sql_select);
?>

<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>위반차량 조회</title>
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
<h2>위반차량 조회</h2>
<table>
  <thead>
  <tr>
    <th>위반 차량 번호</th>
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
<br>
<h2>위반차량 신고</h2>
 <form action="singo.php" method="post">
            <table>
                <tr>
                    <td>차량번호를 입력해주세요</td>
                    <td><input type="text" name="idfee"></td>
                </tr>
                <tr>
                    <td>과태료를 입력해주세요</td>
                    <td><input type="text" name="feemoney"></td>
                </tr>
                <tr>
                    <td>날짜를 입력해주세요</td>
                    <td><input type="date" name="date"></td>
                </tr>
            </table>
            <input type="submit" value="신고 등록">
            <input type="reset" value="다시 입력하기">
        </form>
</body>
</html>