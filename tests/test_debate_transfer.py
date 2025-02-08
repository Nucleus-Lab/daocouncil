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

def test_successful_fund_transfer():
    """Test a successful debate that results in a fund transfer."""
    try:
        FUNDING_AMOUNT_FOR_CDP_WALLET = 0.0001
            
        FUNDING_PROPOSED = 0.0001

        FUNDING_AMOUNT_FOR_PRIVY_WALLET = FUNDING_PROPOSED
        
        TARGET_ADDRESS = "0xBd606164D19e32474CCBda3012783B218E10E52e"
        

        # Initialize debate manager
        debate_id = "fund_transfer_001"
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
        has_funds, balance = manager.check_funding_status(
            wallet_address=wallet_info['cdp_wallet_address'],
            required_amount_eth=FUNDING_AMOUNT_FOR_CDP_WALLET
        )
        if not has_funds:
            logger.error(f"CDP wallet does not have sufficient gas. Current balance: {balance} ETH")
            print("\nPlease ensure the CDP wallet has sufficient gas before continuing.")
            sys.exit(1)
        
        # Prompt for Privy vault funding
        print("\nStep 4: Fund Privy vault for debate")
        prompt_for_funding(
            wallet_address=wallet_info['privy_wallet_address'],
            amount=FUNDING_AMOUNT_FOR_PRIVY_WALLET,
            purpose="Privy vault (for debate funding)"
        )
        

        # Step 5: Check Privy vault funding
        logger.info(f"\nChecking Privy vault funding status for {FUNDING_AMOUNT_FOR_PRIVY_WALLET} ETH...")

        has_funds, balance = manager.check_funding_status(
            wallet_address=wallet_info['privy_wallet_address'],
            required_amount_eth=FUNDING_AMOUNT_FOR_PRIVY_WALLET
        )
        logger.info(f"Has required funds: {has_funds}")
        logger.info(f"Current balance: {balance} ETH")
        

        if not has_funds:
            logger.error("Privy vault does not have sufficient funds")
            print("\nPlease ensure the Privy vault has sufficient funds before continuing.")
            sys.exit(1)
        
        # Record initial balances
        logger.info("\nRecording initial balances...")
        _, privy_initial_balance = manager.check_funding_status(
            wallet_address=wallet_info['privy_wallet_address'],
            required_amount_eth=0  # Just to get balance
        )
        _, target_initial_balance = manager.check_funding_status(
            wallet_address=TARGET_ADDRESS,  # Target address
            required_amount_eth=0  # Just to get balance
        )

        logger.info(f"Initial Privy vault balance: {privy_initial_balance} ETH")
        logger.info(f"Initial target wallet balance: {target_initial_balance} ETH")
        
        # Step 6: Process debate result
        logger.info("\nStep 6: Processing debate result...")
        
        # Sample debate history
        debate_history = f"""
        Proposer: I propose to transfer {FUNDING_PROPOSED} ETH to address {TARGET_ADDRESS} for community development.
        

        Participant 1: What will these funds be used for specifically?
        Proposer: The funds will be used for:
        1. Smart contract security audit (0.0005 ETH)
        2. Community outreach materials (0.0005 ETH)
        
        Participant 2: Have we vetted the security audit firm?
        Proposer: Yes, they have audited 5 major DeFi protocols and have a strong track record.
        
        Participant 1: Given their track record, I support this proposal.
        Participant 2: The costs seem reasonable, I also support this.
        """
        
        # AI votes and reasoning
        ai_votes = {
            "judge_1": True,
            "judge_2": True,
            "judge_3": False
        }
        
        ai_reasoning = {
            "judge_1": "The proposal has clear allocation of funds and uses a reputable audit firm.",
            "judge_2": "The budget breakdown is reasonable and the team has done proper due diligence.",
            "judge_3": "While the audit firm is reputable, we might want to get more competitive quotes."
        }
        
        # Action prompt for fund transfer
        action_prompt = (
            f"Transfer {FUNDING_PROPOSED} ETH to {TARGET_ADDRESS} for community development. "
            f"This transfer should be made from the Privy wallet using the privy_transfer tool."
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
            
        # Final balance checks
        logger.info("\nChecking final balances...")
        _, privy_final_balance = manager.check_funding_status(
            wallet_address=wallet_info['privy_wallet_address'],
            required_amount_eth=0  # Just to get balance
        )
        _, target_final_balance = manager.check_funding_status(
            wallet_address=TARGET_ADDRESS,  # Target address
            required_amount_eth=0  # Just to get balance
        )
        
        logger.info(f"Final Privy vault balance: {privy_final_balance} ETH")
        logger.info(f"Final target wallet balance: {target_final_balance} ETH")
        
        # Verify transfer
        privy_balance_change = privy_initial_balance - privy_final_balance
        target_balance_change = target_final_balance - target_initial_balance
        
        logger.info("\nVerifying transfer...")
        logger.info(f"Privy vault balance change: -{privy_balance_change} ETH")
        logger.info(f"Target wallet balance change: +{target_balance_change} ETH")
        
        # Check if transfer was successful (accounting for gas fees)
        if abs(target_balance_change - FUNDING_PROPOSED) < 0.00001:  # Small difference for rounding
            logger.info("✓ Transfer successful: Target received the correct amount")
        else:
            logger.warning("! Transfer amount mismatch")
            
        if abs(privy_balance_change - (FUNDING_PROPOSED)) < 0.00001:  # Account for gas
            logger.info("✓ Transfer successful: Privy vault debited the correct amount (including gas)")
        else:
            logger.warning("! Privy vault debit amount mismatch")
            
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting fund transfer debate test...")
    test_successful_fund_transfer() 