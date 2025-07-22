from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from config import SOLANA_RPC
import requests
import random

client = Client(SOLANA_RPC)

def create_wallet():
    kp = Keypair()
    pub = str(kp.pubkey())
    priv = kp.to_base58()
    return pub, priv

def get_balance(pubkey):
    try:
        result = client.get_balance(Pubkey.from_string(pubkey))
        return result.value / 1e9
    except:
        return 0.0

def send_sol(priv_base58, to_address, amount):
    try:
        from solders.keypair import Keypair as KP
        sender = KP.from_base58_string(priv_base58)
        to_pubkey = Pubkey.from_string(to_address)
        lamports = int(amount * 1e9)
        tx = Transaction().add(transfer(TransferParams(from_pubkey=sender.pubkey(), to_pubkey=to_pubkey, lamports=lamports)))
        client.send_transaction(tx, sender)
        return f"https://solscan.io/account/{to_address}"
    except Exception as e:
        return f"❌ Error: {e}"

def format_usd_value(sol_amount):
    sol_price = get_sol_price()
    return round(sol_amount * sol_price, 2)

def get_sol_price():
    try:
        data = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd").json()
        return data["solana"]["usd"]
    except:
        return 0

# Dummy list of wallet + Twitter alert events
def tracked_wallets():
    events = [
        "🐳 Wallet 0xabc sniped a CA in 0.3s!",
        "💸 Wallet 0xdef sold early, +220% gain!",
        "📈 Wallet 0x123 bought a new meme coin."
    ]
    return random.sample(events, k=min(3, len(events)))

def tracked_tweets():
    tweets = [
        "🔥 @elonmusk tweeted about 'Doge20X'!",
        "🚨 @FrankDeGods hyped a new SOL CA.",
        "🧠 @CryptoKaleo said 'Buy the dip!'"
    ]
    return random.sample(tweets, k=min(3, len(tweets)))
