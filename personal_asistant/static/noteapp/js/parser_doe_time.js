document.addEventListener("DOMContentLoaded", function () {
  const hourSlider = document.getElementById("hours");
  const minuteSlider = document.getElementById("minutes");
  const hourValue = document.getElementById("hourValue");
  const minuteValue = document.getElementById("minuteValue");
  const enableTimeCheckbox = document.getElementById("enableTime");

  // Перевірка, чи існує глобальна змінна window.dueTime
  if (window.dueTime) {
    const [h, m] = window.dueTime.split(":");
    if (hourSlider && minuteSlider && hourValue && minuteValue && enableTimeCheckbox) {
      hourSlider.value = parseInt(h);
      minuteSlider.value = parseInt(m);
      hourValue.textContent = h;
      minuteValue.textContent = m;
      enableTimeCheckbox.checked = true;
    }
  }
});
