import logging
from backend.debate_manager.debate_manager import DebateManager
import time
import sys


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def prompt_for_funding(wallet_address: str, amount: float, purpose: str) -> None:
    """Prompt user to send funds and wait for confirmation."""
    print("\n" + "="*80)
    print(f"Please send {amount} ETH to the following {purpose}:")
    print(f"Address: {wallet_address}")
    print("="*80)
    
    while True:
        response = input("\nHave you sent the funds? (yes/no): ").lower()
        if response == 'yes':
            print("Proceeding with the test...")
            break
        elif response == 'no':
            print("Please send the funds to continue...")
            time.sleep(5)
        else:
            print("Please answer 'yes' or 'no'")

def test_nft_deployment_debate():
    """Test a debate about NFT deployment that gets rejected."""
    try:        
        FUNDING_AMOUNT_FOR_CDP_WALLET = 0.0001
        FUNDING_AMOUNT_FOR_PRIVY_WALLET = 0.0001
        
        # Initialize debate manager
        debate_id = "nft_deploy_001"
        manager = DebateManager(debate_id=debate_id, api_url="http://localhost:8000")
        
        # Step 1: Initialize debate and create wallets
        logger.info("Step 1: Initializing debate...")
        wallet_info = manager.initialize_debate()
        logger.info(f"Wallet Info: {wallet_info}")
        
        # Prompt for CDP wallet gas funding
        print("\nStep 2: Fund CDP wallet with gas")
        prompt_for_funding(
            wallet_address=wallet_info['cdp_wallet_address'],
            amount=FUNDING_AMOUNT_FOR_CDP_WALLET,
            purpose="CDP wallet (for gas fees)"
        )
        
        # Step 3: Check CDP wallet funding
        logger.info("\nChecking CDP wallet funding...")
        has_funds, balance = manager.check_funding_status(wallet_info['cdp_wallet_address'], FUNDING_AMOUNT_FOR_CDP_WALLET)
        if not has_funds:
            logger.error(f"CDP wallet does not have sufficient gas. Current balance: {balance} ETH")
            print("\nPlease ensure the CDP wallet has sufficient gas before continuing.")
            sys.exit(1)
        
        # Prompt for Privy vault funding
        print("\nStep 4: Fund Privy vault for gas fees")
        prompt_for_funding(
            wallet_address=wallet_info['privy_wallet_address'],
            amount=FUNDING_AMOUNT_FOR_PRIVY_WALLET,
            purpose="Privy vault (for gas fees)"
        )
        
        # Step 5: Check Privy vault funding
        required_amount = FUNDING_AMOUNT_FOR_PRIVY_WALLET
        logger.info(f"\nChecking Privy vault funding status for {required_amount} ETH...")
        has_funds, balance = manager.check_funding_status(wallet_info['privy_wallet_address'], required_amount)
        logger.info(f"Has required funds: {has_funds}")
        logger.info(f"Current balance: {balance} ETH")
        
        if not has_funds:
            logger.error("Privy vault does not have sufficient funds for gas")
            print("\nPlease ensure the Privy vault has sufficient gas fees before continuing.")
            sys.exit(1)
        
        # Step 6: Process debate result
        logger.info("\nStep 6: Processing debate result...")
        
        # Sample debate history
        debate_history = """
        Proposer: I propose to deploy a new NFT collection for our DAO members with the following features:
        - 10,000 total supply
        - 0.05 ETH mint price
        - Special governance rights for holders
        
        Participant 1: What's the utility beyond governance?
        Proposer: Holders will get:
        1. Access to exclusive Discord channels
        2. Priority in future airdrops
        3. Revenue sharing from protocol fees
        
        Participant 2: The market is saturated with NFTs. How is this different?
        Proposer: Our NFTs have actual utility through governance and revenue sharing.
        
        Participant 3: The timing seems wrong with current market conditions.
        Participant 1: I agree, maybe we should wait for better market conditions.
        """
        
        # AI votes and reasoning (majority against)
        ai_votes = {
            "judge_1": False,
            "judge_2": False,
            "judge_3": True
        }
        
        ai_reasoning = {
            "judge_1": "Current market conditions are not favorable for a new NFT launch.",
            "judge_2": "The proposal lacks detailed tokenomics and revenue sharing mechanism.",
            "judge_3": "The governance utility is valuable and could benefit the DAO."
        }
        
        # Action prompt for NFT deployment
        action_prompt = (
            "Deploy a new NFT collection with the following parameters:\n"
            "- Name: 'DAO Governance NFT'\n"
            "- Symbol: 'DAOG'\n"
            "- Total Supply: 10000\n"
            "- Mint Price: 0.05 ETH\n"
            "- Features: Governance rights, revenue sharing, exclusive access"
        )
        
        # Process the result
        result = manager.process_debate_result(
            debate_history=debate_history,
            ai_votes=ai_votes,
            ai_reasoning=ai_reasoning,
            action_prompt=action_prompt
        )
        
        # Print results
        logger.info("\nDebate Processing Results:")
        for key, value in result.items():
            logger.info(f"\n{key.replace('_', ' ').title()}:")
            logger.info(f"{value}")
            
        # Note: Since this debate is rejected, no action should be taken
        # but an NFT recording the debate and decision should still be minted
        
        logger.info("\nVerifying no action was taken...")
        final_has_funds, final_balance = manager.check_funding_status(wallet_info['privy_wallet_address'], required_amount)
        logger.info(f"Final balance: {final_balance} ETH")
        if abs(final_balance - balance) < 0.00001:  # Small difference for gas fees
            logger.info("✓ No significant balance change (only gas fees)")
        else:
            logger.warning("! Unexpected balance change detected")
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting NFT deployment debate test...")
    test_nft_deployment_debate() 