document.addEventListener("DOMContentLoaded", function () {
  const hourSlider = document.getElementById("hours");
  const minuteSlider = document.getElementById("minutes");
  const hourValue = document.getElementById("hourValue");
  const minuteValue = document.getElementById("minuteValue");
  const hiddenInput = document.getElementById("due_time");
  const enableTimeCheckbox = document.getElementById("enableTime");

  if (!hourSlider || !minuteSlider || !hourValue || !minuteValue || !hiddenInput || !enableTimeCheckbox) return;

  function updateTime() {
    const h = String(hourSlider.value).padStart(2, "0");
    const m = String(minuteSlider.value).padStart(2, "0");

    hourValue.textContent = h;
    minuteValue.textContent = m;

    hiddenInput.value = enableTimeCheckbox.checked ? `${h}:${m}` : "";
  }

  hourSlider.addEventListener("input", updateTime);
  minuteSlider.addEventListener("input", updateTime);
  enableTimeCheckbox.addEventListener("change", () => {
    const disabled = !enableTimeCheckbox.checked;
    hourSlider.disabled = disabled;
    minuteSlider.disabled = disabled;
    updateTime();
  });

  // Ініціалізація при завантаженні
  const initialDisabled = !enableTimeCheckbox.checked;
  hourSlider.disabled = initialDisabled;
  minuteSlider.disabled = initialDisabled;
  updateTime();
});
