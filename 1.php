<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Document</title>
  <style>
    body {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      background-image: url('https://bferum.co.kr/%EC%9E%A5%EC%95%A0%EC%9D%B8%EC%A3%BC%EC%B0%A8%EA%B5%AC%EC%97%AD/%E2%88%9A%ED%95%9C%EC%9D%BC%EC%8B%9C%EB%A9%98%ED%8A%B8_2020(2).jpg');
      background-repeat: no-repeat;
      background-size: cover;
    }
    
    .login-form {
      background-color: white;
      padding: 20px;
      border-radius: 5px;
      text-align: center;
    }

    .logo-image {
      display: block;
      margin: 0 auto 20px;
      width: 100px; /* 이미지의 크기를 반으로 조정 */
    }
  </style>
</head>

<body>
  <section class="login-form">
    <img class="logo-image" src="https://cdn-icons-png.flaticon.com/512/2760/2760618.png" alt="Logo">
    <h1>장애인 주차구역 관리 시스템<br>LOGIN PAGE</h1>
    <form method="post" action="2.php">
      <div class="int-area">
        <input type="text" name="id" id="id" autocomplete="off" required>
        <label for="id">USER NAME</label>
      </div>

      <div class="int-area">
        <input type="password" name="pw" id="pw" autocomplete="off" required>
        <label for="pw">PASSWORD</label>
      </div>

      <div class="btn-area">
        <button type="submit">LOGIN</button>
      </div>
    </form>
  </section>
</body>
</html>
