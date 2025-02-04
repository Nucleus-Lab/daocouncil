import React, { useState } from 'react';
import { privyWallet } from '../utils/privyWallet';

export const PrivyWalletDemo: React.FC = () => {
    const [walletAddress, setWalletAddress] = useState<string>('');
    const [balance, setBalance] = useState<string>('');
    const [recipientAddress, setRecipientAddress] = useState<string>('');
    const [amount, setAmount] = useState<string>('');
    const [status, setStatus] = useState<string>('');

    const createWallet = async () => {
        setStatus('Creating wallet...');
        const result = await privyWallet.createWallet();
        if (result.success && result.address) {
            setWalletAddress(result.address);
            setStatus('Wallet created successfully!');
            // 获取余额
            const balanceResult = await privyWallet.getBalance(result.address);
            if (balanceResult.success) {
                setBalance(balanceResult.balance.toString());
            }
        } else {
            setStatus(`Failed to create wallet: ${result.error}`);
        }
    };

    const sendTransaction = async () => {
        if (!walletAddress || !recipientAddress || !amount) {
            setStatus('Please fill in all fields');
            return;
        }

        setStatus('Sending transaction...');
        const result = await privyWallet.sendTransaction({
            walletAddress,
            to: recipientAddress,
            value: amount,
        });

        if (result.success) {
            setStatus(`Transaction sent successfully! Hash: ${result.transactionHash}`);
            // 更新余额
            const balanceResult = await privyWallet.getBalance(walletAddress);
            if (balanceResult.success) {
                setBalance(balanceResult.balance.toString());
            }
        } else {
            setStatus(`Failed to send transaction: ${result.error}`);
        }
    };

    return (
        <div className="p-4 max-w-md mx-auto">
            <h2 className="text-2xl font-bold mb-4">Privy Server Wallet Demo</h2>
            
            <div className="mb-4">
                <button
                    onClick={createWallet}
                    className="bg-blue-500 text-white px-4 py-2 rounded"
                    disabled={!!walletAddress}
                >
                    Create Wallet
                </button>
            </div>

            {walletAddress && (
                <>
                    <div className="mb-4">
                        <p>Wallet Address: {walletAddress}</p>
                        <p>Balance: {balance} ETH</p>
                    </div>

                    <div className="mb-4">
                        <input
                            type="text"
                            placeholder="Recipient Address"
                            value={recipientAddress}
                            onChange={(e) => setRecipientAddress(e.target.value)}
                            className="w-full p-2 border rounded mb-2"
                        />
                        <input
                            type="text"
                            placeholder="Amount (ETH)"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            className="w-full p-2 border rounded mb-2"
                        />
                        <button
                            onClick={sendTransaction}
                            className="bg-green-500 text-white px-4 py-2 rounded"
                        >
                            Send Transaction
                        </button>
                    </div>
                </>
            )}

            {status && (
                <div className="mt-4 p-2 rounded bg-gray-100">
                    <p>{status}</p>
                </div>
            )}
        </div>
    );
};

export default PrivyWalletDemo;
