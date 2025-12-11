// main.js - ボタンで挨拶を表示するだけの簡単スクリプト
document.getElementById("helloBtn").addEventListener("click", () => {
  const btn = document.getElementById("helloBtn");
  btn.classList.add("explode");
  btn.innerText = "💥 BOOM!! 💥";

  setTimeout(() => {
    btn.style.display = "none";
  }, 600);
});

document.getElementById("helloBtn").addEventListener("click", () => {
  // 犬を10匹走らせる
  for (let i = 0; i < 10; i++) {
    createDog(i * 200); // ずらして登場
  }
});

function createDog(delay) {
  const dog = document.createElement("img");
  dog.src = "dog.png";
  dog.classList.add("dog");
  dog.style.animationDelay = delay + "ms";

  document.body.appendChild(dog);

  // 走り終わった犬を自動で消す
  setTimeout(() => {
    dog.remove();
  }, 5000);
}
