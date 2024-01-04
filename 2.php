<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <style>
    body  {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      background-image: url('https://bferum.co.kr/%EC%9E%A5%EC%95%A0%EC%9D%B8%EC%A3%BC%EC%B0%A8%EA%B5%AC%EC%97%AD/%E2%88%9A%ED%95%9C%EC%9D%BC%EC%8B%9C%EB%A9%98%ED%8A%B8_2020(2).jpg');
      background-repeat: no-repeat;
      background-size: cover;
    }

    .container {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      background-color: white;
      padding: 20px;
      border-radius: 5px;
      max-width: 400px; /* 가로 길이 조정 */
      width: 80%; /* 가로 길이를 화면 너비에 상대적으로 조정 */
    }

    .container a, .container button {
      margin-bottom: 10px;
    }
  .logo-image {
      display: block;
      margin: 0 auto 20px;
      width: 100px; /* 이미지의 크기를 반으로 조정 */
    }
  </style>
</head>
<body>
  <div class="container">
 <img class="logo-image" src="https://cdn-icons-png.flaticon.com/512/2760/2760618.png" alt="Logo">
    <h1>환영합니다.</h1>
    <br><br>
    <a href="select.php">1. 위반차량 조회 및 신고</a>
    <br>
    <a href="fee.php">2. 신고완료 차량 조회</a>
    <br>
    <a href="3.php">3. 당일 주차 차량 조회</a>
    <br><br>
    <button onclick="location.href='1.php'">로그인 페이지로</button>
  </div>
</body>
</html>
