
// Buy js script

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
function checkMarketAccess(){
    const currntStatus =localStorage.getItem('market_status');
    const buyBtn = doument.querySelector('.btn-buy');
    const sellBtn = document.querySelector('.btn-sell');

    if (currntStatus === "HALTED") {
        buyBtn.disabled = true;
        sellBtn.disabled = true;
        buyBtn.innerText = "Market Halted";
}
}
window.onload = checkMarketAccess;

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

//admin tool js script 

let plaformStats = {
    totalVloume: 5420.50,
    activeUsers: 12,
    inventoryShares: 500
};

const volumeDisplay = document.getElementById('total-volume');
const userDisplay = document.getElementById('user-count');
const adminSharesInput = document.getElementById('admin-shares');
const updateBth = document.getElementById('.inventory-section .btn');

function refershDashboard() {
    volumeDisplay.innerText = '$${platformStats.totalVolume. toFixed(2)}';
    userDisplay.innerText = plaformStats.activeUsers;
}

function toggleMarket(status) {
    localStorage.setItem('market_status', status);
    console.log("Market status update to: " + status);
}

function handleInventoryUpdate() {
    const newShares = parseInt(adminSharesInput.value);

    if (isNaN(newShares) || newShares <= 0) {
        alert("Please enter a valid number of shares to add.");
        return;
    }
    plaformStats.inventoryShares += newShares;
    alert('Success! Added ${newShares} shares. Total inventory: ${platformStats.inventoryShares}');
    
    adminSharesInput.value = '';
}
    updateBth.addEventListener('click', handleInventoryUpdate);
    const menuItems = document.querySelectorAll('.admin-sidebar li a');
    menuItems.forEach(item => {
        item.addEventListener('clik', (e) => {
            console.log('Navigating to: ${item.innerText}');
        });
    });
    refershDashboard();


    // User Audit 

    const users = [
        { id: "P101", name: "Arya", lastAction: "Buy H01", status: "Active", balance: "$1,456.00"},
        { id: "P102", name: "Ayele", lastAction: "Login", status: "Active", balance: "$969.66" },
        { id: "P103", name: "Sam", lastAction: "Buy H04", status: "Active", balance: "$456.35" },
        { id: "P104", name: "Guest-User", lastAction: "Invalid Buy", status: "Flagged", balance: "$0.00" }    
    ];
    function loadAuditTable(){
        const body = document.getElementById('audit-body');
        const totalCount = document.getElementById('totalAccounts');
        const flaggedCount = document.getElementById('flaggedCount');
        
        let flagged = 0;
        totalCount.innerText = users.length;

        body.innerHTML = users.map(user => {
            if(user.status === "Flagged") flagged++;

            return`
                  <tr>
                      <td>${user.id}</td>
                      <td><strong>${user.name}</strong></td>
                      <td>${user.lastAction}</td>
                      <td><span class="status status-${user.status.toLowerCase()}">${user.status}</span></td>
                      <td>${user.balance}</td>
                      <td><button onclick="viewDetails('${user.id}')">View History</button>
                  </tr>
            `;
        }).join('');

        flaggedCount.innerText = flagged;
    }
      
        function filterUsers() {
            let input = document.getElementById('userSearch').value.toLowerCase();
            let rows = document.querySelectorAll('#audit-body tr');

            rows.forEach(row => {
                let text = row.innerText.toLowerCase();
                row.style.display = text.includes(input) ? "" : "none";
            });
        }
            function viewDetails(useriId) {
                alert("Loading detailed transaction history for: " + userId);
            }
            document.addEventListener('DOMContentLoaded', loadAuditTable);


            // Market-control.js

            let isHalted = false

            const tickers = [
                { symbol: "P101", name: "High Growth Fund", vol: "High", status: "Active"},
                { symbol: "H105", name: "Stable Bonds", vol: "Low", status: "Active"}
            ];

            function toggleMarket() {
                const btn = document.getElementById('haltBtn');
                const indicator = document.getElementById('market-status-indicator');

                isHalted = !isHalted;

                if (isHalted) {
                    btn.innerText = "Resume Trading"
                    btn.style.background = "#2a9d8f";
                    indicator.innerText = "Market HALTED";
                    indicator.className = "status-halted";
                    logMrketAction("GLOBAL TRADING HALTED BY ADMIN", "ERROR");
                } else {
                    btn.innerText = "Halt Trading";
                    btn.style.background = "#e63946";
                    indicator.innerText = "MARKET OPEN";
                    indicator.className = "status-open";
                    logMrketAction("Global trading resumed.", "SUCCESS");
                }
                 
                localStorage.setItem('marketStatus', isHalted ? 'HALTED' : 'OPEN');
            }

            function updateGlobalPrice() {
                const newPrice = document.getElementById('basePriceInput').value;
                localStorage.setItem('globalStockPrice', newPrice);
                logMrketAction(`Base price adjusted to  $${newPrice}`, "INFO");
                alert("Price updated for all users.");
                }

                function logMarketAction(msg, type) {
                    let log = JSON.parse(localStorage.getItem('systemLogs')) || [];
                    logs.unshift({time: new Date().toLocaleString(), type: type, msg: msg });
                    localStorage.setItem('systemLogs', JSON.stringify(logs));
                }

                function loadTickers() {
                    const body =document.getAnimations('tickerBody');
                    body.innerHTML = tickers.map(t => `
                        <tr>
                        <td><Storng>${t.symbol}</Storng></td>
                        <td>${t.name}</td>
                        <td>${t.vol}</td>
                        <td>${t.status}</td>
                        <td><button onclick="alert('Ticker settings for ${t.symbol}')">Edit</button></td>
                        </tr>
                    `).join('');
                }
            document.addEventListener('DOMContentLoaded', loadTickers);

            // Stock Inventory control js script

            let inventory = { 
                "H01" : { onHnad: 500, reserved: 45},
                "S05" : { onHnad: 1200, reserved: 10}
            };

            function renderInventory() {
                const body = document.getElementById('inventoryBody');
                body.innerHTML = '';

                for (const ticker in inventory) {
                     const data = inventory[ticker];
                     const status = data.onHnad < 100 ? "status-low" : "status-ok";

                 body.innerHTML += `
                 <tr>
                    <td><strong>${ticker}</strong></td>
                    <td>${data.onHnad}</td>
                    <td>${data.reserved}</td>
                    <td class="${status}">${data.onHnad < 100 ? 'LOW' : 'STABLE'}</td>
                 </tr>
                 `;
            }
        }

        function pricessInventoryChange(){
             const ticker = document.getElementById('tickerSelect').value;
             const type = document.getElementById('adjustmentType').value;

             if (isNaN(amount) || amount <= 0) {
                alert("Please enter a valid positive number.");
                return;
             }
             if (type === "add") {
                inventory[ticker].onHnad += amount;
             } else if (type === "subtruct") {
                if (inventory[ticker].onHnad - amount < 0){
                    alert("Insufficient inventory to remove that much!");
                    return;
                } else if (type === "set") {
                    inventory[ticker].onHnad = amount;
                }

                logInventoryAction('Inventory updated for ${ticker}: ${type} ${amount} shares.');

                localStorage.getElementById('shareAmount').value = '';
             }

             function logInventoryAction(msg) {
                let logs = JSON.parse(localStorage.getItem('systemLogs')) || [];
                logs.unshift({time: new Date().toLocaleString(), type: 'INFO', msg: msg});
                localStorage.setItem('systemLogs', JSON.stringify(logs));
             }
        }
            document.addEventListener('DOMContentLoaded', renderInventory);