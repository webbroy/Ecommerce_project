// Auto-fill payment amount when product + quantity are chosen
const productSelect  = document.getElementById('productSelect');
const quantityInput  = document.getElementById('quantityInput');
const amountInput    = document.getElementById('amountInput');

function updateAmount() {
  if (!productSelect || !quantityInput || !amountInput) return;
  const opt = productSelect.options[productSelect.selectedIndex];
  const price = parseFloat(opt?.dataset?.price || 0);
  const qty   = parseInt(quantityInput.value || 0, 10);
  if (price > 0 && qty > 0) {
    amountInput.value = (price * qty).toFixed(2);
  }
}

productSelect?.addEventListener('change', updateAmount);
quantityInput?.addEventListener('input', updateAmount);
