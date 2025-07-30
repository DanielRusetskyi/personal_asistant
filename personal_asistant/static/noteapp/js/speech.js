document.addEventListener("DOMContentLoaded", function () {
  const micBtn = document.getElementById('micBtn');
  const descInput = document.querySelector('textarea[name="description"]');

  if (!micBtn || !descInput) return; // безпечна перевірка

  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'uk-UA';
    recognition.interimResults = false;

    micBtn.addEventListener('click', () => {
      recognition.start();
      micBtn.innerText = '🎙️...';
    });

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      descInput.value += (descInput.value ? ' ' : '') + transcript;
      micBtn.innerText = '🎤';
    };

    recognition.onerror = (event) => {
      console.error('Speech error:', event.error);
      micBtn.innerText = '🎤';
    };
  } else {
    micBtn.disabled = true;
    micBtn.title = 'Ваш браузер не підтримує голосове введення';
  }
});
