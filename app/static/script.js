const uploadForm = document.getElementById("uploadForm");
const questionForm = document.getElementById("questionForm");
const uploadResult = document.getElementById("uploadResult");
const answerDiv = document.getElementById("answer");

// Handle PDF Upload
uploadForm.onsubmit = async (e) => {
  e.preventDefault();
  const formData = new FormData();
  formData.append("file", document.getElementById("pdfFile").files[0]);

  uploadResult.innerHTML = `<div class="loader"></div><p>Uploading PDF... please wait</p>`;

  try {
    const res = await fetch("/upload_pdf", { method: "POST", body: formData });
    const data = await res.json();

    // Replace loader with success message
    uploadResult.innerHTML = `<p class="success">${data.message}</p>`;

    // Remove success message after 5 seconds
    setTimeout(() => {
      uploadResult.innerHTML = "";
    }, 5000);
  } catch {
    uploadResult.innerHTML = `<p style="color:#FF6B6B;">❌ Error uploading PDF!</p>`;
  }
};

// Handle Question Asking
questionForm.onsubmit = async (e) => {
  e.preventDefault();
  const question = document.getElementById("question").value.trim();
  if (!question) return;

  // Show loader while processing
  answerDiv.innerHTML = `
    <div class="loader"></div>
    <p>Processing your question...</p>
  `;

  const formData = new FormData();
  formData.append("question", question);

  try {
    const res = await fetch("/ask_question", { method: "POST", body: formData });
    const data = await res.json();

    answerDiv.innerHTML = `<p><strong>Answer:</strong> ${data.answer}</p>`;
  } catch {
    answerDiv.innerHTML = `<p style="color:#FF6B6B;">❌ Error fetching answer!</p>`;
  }
};
