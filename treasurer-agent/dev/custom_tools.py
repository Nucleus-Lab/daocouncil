from cdp import Wallet
from cdp_langchain.tools import CdpTool
from pydantic import BaseModel, Field
from typing import Optional

# Define input schemas for our custom tools

class DeployUpdatableNFTInput(BaseModel):
    """Input argument schema for deploying updatable NFT contract."""
    name: str = Field(
        ...,
        description="The name of the NFT collection"
    )
    symbol: str = Field(
        ...,
        description="The symbol of the NFT collection"
    )
    base_uri: str = Field(
        default="",
        description="The base URI for token metadata"
    )

class UpdateNFTMetadataInput(BaseModel):
    """Input argument schema for updating NFT metadata."""
    contract_address: str = Field(
        ...,
        description="The address of the NFT contract"
    )
    token_id: int = Field(
        ...,
        description="The ID of the token to update"
    )
    new_uri: str = Field(
        ...,
        description="The new URI for the token metadata"
    )

class MintUpdatableNFTInput(BaseModel):
    """Input argument schema for minting updatable NFT."""
    contract_address: str = Field(
        ...,
        description="The address of the NFT contract"
    )
    to_address: str = Field(
        ...,
        description="The address to mint the NFT to"
    )
    token_id: int = Field(
        ...,
        description="The token ID to mint"
    )
    token_uri: str = Field(
        ...,
        description="The URI for the token metadata"
    )

# Solidity contract template for updatable NFT
UPDATABLE_NFT_CONTRACT = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract UpdatableNFT is ERC721, Ownable {
    mapping(uint256 => string) private _tokenURIs;
    string private _baseURIextended;

    constructor(string memory name_, string memory symbol_) 
        ERC721(name_, symbol_) {}

    function _baseURI() internal view virtual override returns (string memory) {
        return _baseURIextended;
    }
    
    function setBaseURI(string memory baseURI_) external onlyOwner {
        _baseURIextended = baseURI_;
    }

    function mint(address to, uint256 tokenId) external onlyOwner {
        _safeMint(to, tokenId);
    }

    function _setTokenURI(uint256 tokenId, string memory _tokenURI) internal virtual {
        require(_exists(tokenId), "URI set of nonexistent token");
        _tokenURIs[tokenId] = _tokenURI;
    }

    function setTokenURI(uint256 tokenId, string memory _tokenURI) external onlyOwner {
        _setTokenURI(tokenId, _tokenURI);
    }

    function tokenURI(uint256 tokenId) public view virtual override returns (string memory) {
        require(_exists(tokenId), "URI query for nonexistent token");

        string memory _tokenURI = _tokenURIs[tokenId];
        string memory base = _baseURI();

        if (bytes(_tokenURI).length > 0) {
            return _tokenURI;
        }

        if (bytes(base).length > 0) {
            return string(abi.encodePacked(base, tokenId));
        }

        return "";
    }
}
"""

# Tool functions
def deploy_updatable_nft(wallet: Wallet, name: str, symbol: str, base_uri: str = "") -> str:
    """Deploy a new NFT contract with metadata update capability.
    
    Args:
        wallet (Wallet): The wallet to deploy from
        name (str): The name of the NFT collection
        symbol (str): The symbol of the NFT collection
        base_uri (str, optional): The base URI for token metadata
        
    Returns:
        str: The deployment response with contract address
    """
    try:
        # Deploy the contract
        contract = wallet.deploy_contract(
            UPDATABLE_NFT_CONTRACT,
            constructor_args=[name, symbol]
        ).wait()

        # Define full ABI for the deployed contract
        abi = [
            {
                "inputs": [
                    {"internalType": "string", "name": "name_", "type": "string"},
                    {"internalType": "string", "name": "symbol_", "type": "string"}
                ],
                "stateMutability": "nonpayable",
                "type": "constructor"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
                    {"internalType": "string", "name": "_tokenURI", "type": "string"}
                ],
                "name": "setTokenURI",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "string", "name": "baseURI_", "type": "string"}
                ],
                "name": "setBaseURI",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "tokenId", "type": "uint256"}
                ],
                "name": "mint",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

        # Create contract instance with full ABI
        contract_with_abi = wallet.create_contract(contract.address, abi)

        # Set base URI if provided
        if base_uri:
            contract_with_abi.functions.setBaseURI(base_uri).send().wait()

        return f"""Successfully deployed UpdatableNFT contract:
Contract Address: {contract.address}
Name: {name}
Symbol: {symbol}
Base URI: {base_uri if base_uri else 'Not set'}
ABI: Contract supports: mint(), setTokenURI(), setBaseURI()"""

    except Exception as e:
        return f"Error deploying contract: {str(e)}"

def update_nft_metadata(wallet: Wallet, contract_address: str, token_id: int, new_uri: str) -> str:
    """Update the metadata URI for a specific token.
    
    Args:
        wallet (Wallet): The wallet to send the transaction from
        contract_address (str): The address of the NFT contract
        token_id (int): The ID of the token to update
        new_uri (str): The new URI for the token metadata
        
    Returns:
        str: The transaction response
    """
    try:
        # Define the ABI for the setTokenURI function
        abi = [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
                    {"internalType": "string", "name": "_tokenURI", "type": "string"}
                ],
                "name": "setTokenURI",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        # Create contract instance using low-level interface
        contract = wallet.create_contract(contract_address, abi)
        
        # Update the token URI
        tx = contract.functions.setTokenURI(token_id, new_uri).send().wait()

        return f"""Successfully updated NFT metadata:
Token ID: {token_id}
New URI: {new_uri}
Transaction Hash: {tx.hash if hasattr(tx, 'hash') else 'N/A'}"""

    except Exception as e:
        return f"Error updating metadata: {str(e)}"

def mint_updatable_nft(wallet: Wallet, contract_address: str, to_address: str, token_id: int, token_uri: str) -> str:
    """Mint a new token in the updatable NFT contract.
    
    Args:
        wallet (Wallet): The wallet to mint from
        contract_address (str): The address of the NFT contract
        to_address (str): The address to mint the NFT to
        token_id (int): The token ID to mint
        token_uri (str): The URI for the token metadata
        
    Returns:
        str: The minting response
    """
    try:
        # Define the ABI for mint and setTokenURI functions
        abi = [
            {
                "inputs": [
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "tokenId", "type": "uint256"}
                ],
                "name": "mint",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
                    {"internalType": "string", "name": "_tokenURI", "type": "string"}
                ],
                "name": "setTokenURI",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        # Create contract instance
        contract = wallet.create_contract(contract_address, abi)
        
        # Mint the token
        mint_tx = contract.functions.mint(to_address, token_id).send().wait()
        
        # Set the token URI
        uri_tx = contract.functions.setTokenURI(token_id, token_uri).send().wait()

        return f"""Successfully minted NFT:
Contract Address: {contract_address}
Token ID: {token_id}
Owner: {to_address}
Token URI: {token_uri}
Mint Transaction: {mint_tx.hash if hasattr(mint_tx, 'hash') else 'N/A'}
URI Transaction: {uri_tx.hash if hasattr(uri_tx, 'hash') else 'N/A'}"""

    except Exception as e:
        return f"Error minting NFT: {str(e)}"

# Create tool instances
def get_custom_tools(agentkit):
    """Get the custom tools for the agent.
    
    Args:
        agentkit: The CDP Agentkit wrapper instance
        
    Returns:
        list: List of custom tools
    """
    deploy_nft_tool = CdpTool(
        name="deploy_updatable_nft",
        description="""Deploy a new NFT contract with metadata update capability. 
        This contract allows minting NFTs and updating their metadata later.""",
        cdp_agentkit_wrapper=agentkit,
        args_schema=DeployUpdatableNFTInput,
        func=deploy_updatable_nft,
    )

    mint_nft_tool = CdpTool(
        name="mint_updatable_nft",
        description="Mint a new token in an updatable NFT contract and set its initial metadata.",
        cdp_agentkit_wrapper=agentkit,
        args_schema=MintUpdatableNFTInput,
        func=mint_updatable_nft,
    )

    update_metadata_tool = CdpTool(
        name="update_nft_metadata",
        description="Update the metadata URI for a specific token in an updatable NFT contract.",
        cdp_agentkit_wrapper=agentkit,
        args_schema=UpdateNFTMetadataInput,
        func=update_nft_metadata,
    )

    return [deploy_nft_tool, mint_nft_tool, update_metadata_tool] 