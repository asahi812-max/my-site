// main.js - ボタンで挨拶を表示するだけの簡単スクリプト
document.addEventListener("DOMContentLoaded", function() {
  const btn = document.getElementById("helloBtn");
  const res = document.getElementById("helloResult");
  btn.addEventListener("click", function() {
    res.textContent = "こんにちは。自己紹介ページを見てくれてありがとう。";
  });
});