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
  dog.src = "dog-run.png";
  dog.classList.add("run-dog");
  dog.style.animationDelay = delay + "ms";

  document.body.appendChild(dog);

  // 走り終わった犬を自動で消す
  setTimeout(() => {
    dog.remove();
  }, 5000);
}

document.addEventListener("mousemove", (e) => {
  const trail = document.createElement("div");
  trail.classList.add("cursor-trail");

  trail.style.left = e.clientX + "px";
  trail.style.top = e.clientY + "px";

  document.body.appendChild(trail);

  // 消えるアニメ後に削除
  setTimeout(() => {
    trail.remove();
  }, 600);
});
