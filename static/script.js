setTimeout(() => {
document.querySelectorAll('.flash-message').forEach(el => {
  el.style.transition = "opacity 0.5s";
  el.style.opacity = '0';
  setTimeout(() => el.remove(), 500);
});
}, 4000);
