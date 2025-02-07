import { PrivyClient } from '@privy-io/server-auth';
import { PRIVY_CONFIG } from '../config/privy';

class PrivyWallet {
    private static instance: PrivyWallet;
    private client: PrivyClient;

    private constructor() {
        this.client = new PrivyClient({
            appId: PRIVY_CONFIG.appId,
            appSecret: PRIVY_CONFIG.appSecret,
        });
    }

    public static getInstance(): PrivyWallet {
        if (!PrivyWallet.instance) {
            PrivyWallet.instance = new PrivyWallet();
        }
        return PrivyWallet.instance;
    }

    // 创建新钱包
    public async createWallet() {
        try {
            const wallet = await this.client.createWallet();
            return {
                success: true,
                address: wallet.address,
                wallet
            };
        } catch (error) {
            console.error('Failed to create wallet:', error);
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error'
            };
        }
    }

    // 发送交易
    public async sendTransaction(params: {
        walletAddress: string;
        to: string;
        value: string;
        chain?: string;
    }) {
        try {
            const { walletAddress, to, value, chain = 'ethereum' } = params;
            
            // 创建交易
            const transaction = await this.client.createTransaction({
                walletAddress,
                chain,
                to,
                value,
            });

            // 提交交易
            const txHash = await this.client.submitTransaction(transaction.id);

            return {
                success: true,
                transactionHash: txHash,
                transaction
            };
        } catch (error) {
            console.error('Failed to send transaction:', error);
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error'
            };
        }
    }

    // 获取钱包余额
    public async getBalance(walletAddress: string, chain: string = 'ethereum') {
        try {
            const balance = await this.client.getWalletBalance({
                walletAddress,
                chain,
            });

            return {
                success: true,
                balance
            };
        } catch (error) {
            console.error('Failed to get balance:', error);
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error'
            };
        }
    }
}

export const privyWallet = PrivyWallet.getInstance();
