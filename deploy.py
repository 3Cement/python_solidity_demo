from solcx import compile_standard
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile Our Solidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.10",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to Sepolia Testnet
w3 = Web3(
    Web3.HTTPProvider(
        "https://eth-sepolia.g.alchemy.com/v2/FqNMCQajpWEclzM-scbxZd1bNHf2UvfW"
    )
)
chain_id = 11155111
my_address = "0xdBBc3C70044863228803889983a646C647ee88Da"
private_key = os.getenv("PRIVATE_KEY")

# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.get_transaction_count(my_address)

# 1. Build a transaction
# 2. Sign a trnsaction
# 3. Send a transaction
transaction = SimpleStorage.constructor().build_transaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# Send this signed transaction
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed on address: {0}".format(tx_receipt.contractAddress))
# Working with the contract
# Contract Address
# Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Call -> Simulate making the call and getting a return value
# Transact -> Actually make a state change

# Initial value of favorite number
print(simple_storage.functions.retrieve().call())
print("Updating Contract")
# Create Transaction
store_transaction = simple_storage.functions.store(15).build_transaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)
# Sign Transaction
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
# Send Transaction
send_Store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
# Wait for transaction
tx_receipt = w3.eth.wait_for_transaction_receipt(send_Store_tx)
print("Updated!")
print(simple_storage.functions.retrieve().call())
