const STOCK_PRICE = 182.45;
const sharesInput = document.getElementById('shares');
const totalDisplay = document.getElementById('total');
const buyBtn = document.getElementById('buy-btn')
const sellBtn = document.getElementById('sell-btn')

//Calculate Total in real-time 

function updateEstimate(){
    const shares = parseFloat(sharesInput.value) || 0;
    const total = (shares * STOCK_PRICE). toFixed(2);
     totalDisplay.innerText = `$${total}`;
}

// Handle order Submission

function processOrder(action) {
    const shares = parseFloat(sharesInput.value);
    
    if (!shares || shares <= 0) {
        alert("Please enter a valid quantity of shares.");
        return;
    }
    const confirmTrade = confirm( `Confirm ${action} order for ${shares} shares?`);
    if (confirmTrade) {
        console.log(`Executing $ {action} for ${shares} units...`);
        alert(`Success: ${action} order placed!`);

        // Reset form

        sharesInput.value= '';
        updateEstimate();
    }
}

// Event listeners

sharesInput.addEventListener('input', updateEstimate);
buyBtn.addEventListener('click', () => processOrder('BUY'));
sellBtn.addEventListener('click', () => processOrder('SELL'));

