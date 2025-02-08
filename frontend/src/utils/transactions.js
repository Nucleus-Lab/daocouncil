import { parseEther } from 'viem';
import { API_CONFIG } from '../config/api';

/**
 * Checks if MetaMask is properly connected and unlocked
 * @param {Object} provider - The Web3 provider (window.ethereum)
 * @returns {Promise<boolean>} True if connected and unlocked
 */
const ensureWalletConnected = async (provider) => {
    try {
        // Request accounts to ensure connection
        const accounts = await provider.request({ method: 'eth_requestAccounts' });
        return accounts && accounts.length > 0;
    } catch (error) {
        console.error('Error connecting to wallet:', error);
        return false;
    }
};

/**
 * Sends funds to a target wallet using the connected Web3 wallet
 * @param {Object} provider - The Web3 provider (window.ethereum)
 * @param {string} targetAddress - The address to send funds to
 * @param {number} amount - Amount in ETH to send
 * @param {string} purpose - Purpose of the funding (for display)
 * @returns {Promise<string>} Transaction hash
 */
export const fundWallet = async (provider, targetAddress, amount, purpose) => {
    try {
        console.log(`Initiating funding process for ${purpose}`);
        console.log('Parameters:', { targetAddress, amount, purpose });

        // Ensure wallet is connected
        console.log('Checking wallet connection...');
        const isConnected = await ensureWalletConnected(provider);
        if (!isConnected) {
            throw new Error('Please unlock your wallet and try again');
        }

        // Get connected accounts
        console.log('Requesting accounts...');
        const accounts = await provider.request({ method: 'eth_requestAccounts' });
        const fromAddress = accounts[0];
        console.log('Connected from address:', fromAddress);

        // Convert amount to Wei and then to hex
        const amountInWei = parseEther(amount.toString());
        const amountInHex = `0x${amountInWei.toString(16)}`;
        console.log('Amount in Wei:', amountInWei.toString());
        console.log('Amount in Hex:', amountInHex);

        // First estimate gas
        console.log('Estimating gas...');
        const gasEstimate = await provider.request({
            method: 'eth_estimateGas',
            params: [{
                from: fromAddress,
                to: targetAddress,
                value: amountInHex
            }]
        });
        console.log('Gas estimate:', gasEstimate);

        // Prepare transaction request
        const transactionRequest = {
            from: fromAddress,
            to: targetAddress,
            value: amountInHex,
            gas: gasEstimate
        };
        
        console.log('Transaction request:', transactionRequest);

        // Request transaction with retry logic
        let attempts = 0;
        const maxAttempts = 3;
        
        while (attempts < maxAttempts) {
            try {
                console.log(`Attempt ${attempts + 1} of ${maxAttempts}`);
                console.log('Sending transaction request to provider...');
                
                const transactionHash = await provider.request({
                    method: 'eth_sendTransaction',
                    params: [transactionRequest],
                });
                
                console.log(`Transaction hash for ${purpose}:`, transactionHash);
                return transactionHash;
            } catch (error) {
                console.error(`Attempt ${attempts + 1} failed:`, error);
                attempts++;
                
                if (error.code === 4001) {  // User rejected
                    console.log('Transaction rejected by user');
                    throw error;
                }
                
                if (attempts === maxAttempts) {
                    throw error;
                }
                
                console.log('Waiting before retry...');
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                console.log('Attempting to reconnect...');
                await ensureWalletConnected(provider);
            }
        }
    } catch (error) {
        console.error(`Error in fundWallet for ${purpose}:`, error);
        console.error('Error details:', {
            message: error.message,
            code: error.code,
            stack: error.stack
        });
        
        if (error.code === 4001) {
            throw new Error('Transaction was rejected by user');
        }
        
        // Check for specific MetaMask errors
        if (error.code === -32002) {
            throw new Error('MetaMask request already pending. Please check your MetaMask wallet.');
        }
        
        if (error.code === -32603) {
            throw new Error('Internal JSON-RPC error. Please check the console for details.');
        }
        
        throw new Error(`Failed to fund ${purpose}. ${error.message || 'Please ensure your wallet is unlocked and try again.'}`);
    }
};

/**
 * Check the funding status of a debate's wallets
 * @param {string} debateId - The ID of the debate
 * @param {number} requiredAmount - Required amount in ETH
 * @returns {Promise<{success: boolean, cdpFunded: boolean, privyFunded: boolean, message: string}>}
 */
export const checkDebateFundingStatus = async (debateId, requiredAmount) => {
    try {
        console.log('Checking funding status for debate:', debateId);
        const response = await fetch(`${API_CONFIG.BACKEND_URL}/debate/${debateId}/funding_status`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to check funding status');
        }

        const result = await response.json();
        console.log('Funding status result:', result);

        return {
            success: result.cdp_funded && (requiredAmount === 0 || result.privy_funded),
            cdpFunded: result.cdp_funded,
            privyFunded: result.privy_funded,
            message: result.message
        };
    } catch (error) {
        console.error('Error checking funding status:', error);
        throw new Error(`Failed to verify funding status: ${error.message}`);
    }
}; 