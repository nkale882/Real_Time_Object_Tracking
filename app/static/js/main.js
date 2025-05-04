const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let startX, startY, drawing = false;

canvas.addEventListener('mousedown', e => {
  startX = e.offsetX;
  startY = e.offsetY;
  drawing = true;
});

canvas.addEventListener('mousemove', e => {
  if (!drawing) return;
  const w = e.offsetX - startX;
  const h = e.offsetY - startY;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = 'red';
  ctx.lineWidth = 2;
  ctx.strokeRect(startX, startY, w, h);
});

canvas.addEventListener('mouseup', e => {
  drawing = false;
  const w = e.offsetX - startX;
  const h = e.offsetY - startY;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  fetch('/select_box', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      x: startX,
      y: startY,
      w: w,
      h: h,
      canvasWidth: canvas.width,
      canvasHeight: canvas.height
    })
  }).then(res => res.json()).then(data => {
    console.log(data.status);
    console.log("Scaled box sent to backend:", data.scaled_box);
  });
});
