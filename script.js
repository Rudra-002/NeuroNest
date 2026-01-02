document.getElementById("screeningForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const questions = document.querySelectorAll(".question");
const progressText = document.getElementById("progressText");

questions.forEach((q, index) => {
  q.querySelector("select").addEventListener("change", () => {
    progressText.innerText = `Question ${index + 1} of 6`;
  });
});


  const payload = {
    q1: Number(document.getElementById("q1").value),
    q2: Number(document.getElementById("q2").value),
    q3: Number(document.getElementById("q3").value),
    q4: Number(document.getElementById("q4").value),
    q5: Number(document.getElementById("q5").value),
    q6: Number(document.getElementById("q6").value)
  };

  const response = await fetch("http://127.0.0.1:3000/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const result = await response.json();
  localStorage.setItem("screeningResult", JSON.stringify(result));
  window.location.href = "dashboard.html";
});
