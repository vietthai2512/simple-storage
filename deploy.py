import json
import os
from web3 import Web3
from solcx import compile_standard, install_solc
from dotenv import load_dotenv

load_dotenv()
install_solc("0.8.7")

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile sol file
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.8.7",
)

with open("complied_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connect to blockchain
w3 = Web3(Web3.HTTPProvider(os.getenv("HTTP_PROVIDER")))
chain_id = int(os.getenv("CHAIN_ID"))
my_address = os.getenv("MY_ADDRESS")
my_private_key = os.getenv("MY_PRIVATE_KEY")

# Create the contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.get_transaction_count(my_address)

transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)
signed_transaction = w3.eth.account.sign_transaction(transaction, my_private_key)

print("Deploying Contract!")
tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

print("Waiting for transaction to finish...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Done! Contract deployed to {tx_receipt.contractAddress}")

# Working with contract
simple_storage_contract = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(f"Initial Stored Value {simple_storage_contract.functions.retrieve().call()}")
greeting_transaction = simple_storage_contract.functions.store(15).buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)
signed_greeting_txn = w3.eth.account.sign_transaction(
    greeting_transaction, private_key=my_private_key
)
tx_greeting_hash = w3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
print("Updating stored Value...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_greeting_hash)

print(simple_storage_contract.functions.retrieve().call())
