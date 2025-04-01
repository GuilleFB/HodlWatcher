document.addEventListener('DOMContentLoaded', function() {
    // Obtener referencias a los campos del formulario
    const sideSelect = document.getElementById('id_side');
    const currencySelect = document.getElementById('id_currency');
    const paymentMethodSelect = document.getElementById('id_payment_method_id');
    const assetCodeSelect = document.getElementById('id_asset_code');
    const amountInput = document.getElementById('id_amount');
    const rateFeeInput = document.getElementById('id_rate_fee');

    // Función para actualizar el resumen
    function updateSummary() {
        // Obtiene valores de los campos
        const side = sideSelect ? sideSelect.options[sideSelect.selectedIndex]?.text || '' : '';
        const currencyCode = currencySelect ? currencySelect.value || '' : '';
        const paymentMethod = paymentMethodSelect ? paymentMethodSelect.options[paymentMethodSelect.selectedIndex]?.text || '' : '';
        const assetCode = assetCodeSelect ? assetCodeSelect.value || '' : '';
        const amount = amountInput ? amountInput.value || '0' : '0';
        const rateFee = rateFeeInput ? rateFeeInput.value || '0' : '0';

        // Actualiza textos en el resumen
        updateElementText('.summary-side', side);
        updateElementText('.summary-asset', assetCode);
        updateElementText('.summary-currency', currencyCode);
        updateElementText('.summary-payment-method', paymentMethod);
        updateElementText('.summary-amount', amount);
        updateElementText('.summary-rate-fee', rateFee + '%');

        // Actualiza iconos y clases del badge
        const sideBadge = document.querySelector('.side-badge');
        if (sideBadge) {
            // Eliminar clases existentes
            sideBadge.classList.remove('bg-danger', 'bg-success', 'text-danger', 'text-success', 'border-danger', 'border-success');

            // Agregar clases según el valor seleccionado
            if (side === 'Buy') {
                sideBadge.classList.add('bg-danger', 'text-danger', 'border-danger');
            } else {
                sideBadge.classList.add('bg-success', 'text-success', 'border-success');
            }
        }

        // Actualiza el icono de flecha
        const sideIcon = document.querySelector('.side-icon');
        if (sideIcon) {
            sideIcon.classList.remove('bi-arrow-down-circle', 'bi-arrow-up-circle');
            sideIcon.classList.add(side === 'Buy' ? 'bi-arrow-down-circle' : 'bi-arrow-up-circle');
        }

        const currencyFlag = document.querySelector('.currency-flag');
        if (currencyFlag && currencyCode) {
            currencyFlag.className = `fi fi-${currencyCode.slice(0,2).toLowerCase()} fis me-2`;
        }
    }

    // Función auxiliar para actualizar texto de elementos
    function updateElementText(selector, text) {
        const element = document.querySelector(selector);
        if (element) {
            element.textContent = text;
        }
    }

    // Agregar event listeners para los cambios en los campos
    const formFields = [sideSelect, currencySelect, paymentMethodSelect, assetCodeSelect, amountInput, rateFeeInput];
    formFields.forEach(field => {
        if (field) {
            field.addEventListener('change', updateSummary);
        }
    });

    // Inicializa el resumen con los valores actuales después de definir todo
    updateSummary();
});
