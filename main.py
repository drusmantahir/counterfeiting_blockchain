from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from web3 import Web3
import json

app = FastAPI()

# Infura URL for Sepolia testnet
infura_url = "https://sepolia.infura.io/v3/YourProjectKEY"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check connection
if not web3.is_connected():
    raise ConnectionError("Failed to connect to Ethereum Sepolia testnet")

# Replace with the actual contract address
contract_address = '0xaAbd613A609c4A1e7bAb6DF3eFdA3dC3Fe0ed9fb'

# ABI for the KeyGen contract
contract_abi = json.loads("""
[
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_key",
                "type": "string"
            }
        ],
        "name": "addKey",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_key",
                "type": "string"
            }
        ],
        "name": "consumeKey",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_key",
                "type": "string"
            }
        ],
        "name": "isKeyConsumed",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getOwner",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]
""")

# Create the contract object
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

class KeyQuery(BaseModel):
    key: str


# Define the request model
class AddKeyRequest(BaseModel):
    new_key: str


@app.get("/key-status/{key}", response_model=dict)
async def get_key_status(key: str):
    try:
        is_consumed = contract.functions.isKeyConsumed(key).call()
        return {"key": key, "is_consumed": is_consumed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contract-owner", response_model=dict)
async def get_contract_owner():
    try:
        owner_address = contract.functions.getOwner().call()
        return {"owner": owner_address}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-key/")
async def add_key(request: AddKeyRequest):
    try:
        # Define the account details
        from_account = ""  # Replace with your Ethereum wallet address
        private_key = ""      # Replace with your private key
        new_key = request.new_key

        # Example of adjusted gas price and limit
        gas_price = web3.to_wei('20', 'gwei')  # Lower gas price estimate
        gas_limit = 1000000  # Estimate gas limit


        # Add a new key
        #new_key = "304502202c993eed06344b5b72b688a966ebbd824ba76d45ad84a0ea1eaa9f577c164d98022100d5ecfc07c88a666d3a2003dc6d6ceda472575011d491b8915e565f2780e1171e"
        transaction = contract.functions.addKey(new_key).build_transaction({
            'from': from_account,
            'nonce': web3.eth.get_transaction_count(from_account),
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': 11155111  # Sepolia chain ID
        })

        # Sign the transaction
        signed_tx = web3.eth.account.sign_transaction(transaction, private_key)

        # Send the transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Wait for the transaction receipt
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction successful with hash: {tx_receipt.transactionHash.hex()}")

        return {"transaction_hash": tx_receipt.transactionHash.hex()}
    
    except AttributeError as e:
        raise HTTPException(status_code=400, detail=f"Attribute error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    

@app.post("/consume-key/")
async def add_key(request: AddKeyRequest):
    try:
        # Define the account details
        from_account = ""  # Replace with your Ethereum wallet address
        private_key = ""      # Replace with your private key
        key_to_consume = request.new_key

        # Example of adjusted gas price and limit
        gas_price = web3.to_wei('20', 'gwei')  # Lower gas price estimate
        gas_limit = 1000000  # Estimate gas limit


        transaction = contract.functions.consumeKey(key_to_consume).build_transaction({
            'from': from_account,
            'nonce': web3.eth.get_transaction_count(from_account),
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': 11155111  # Sepolia chain ID
        })

        # Sign the transaction
        signed_tx = web3.eth.account.sign_transaction(transaction, private_key)

        # Send the transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Wait for the transaction receipt
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction successful with hash: {tx_receipt.transactionHash.hex()}")

        return {"transaction_hash": tx_receipt.transactionHash.hex()}
    
    except AttributeError as e:
        raise HTTPException(status_code=400, detail=f"Attribute error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
