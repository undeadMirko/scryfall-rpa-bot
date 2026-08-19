import pandas as pd
import os
import sys

# Ensure src modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from src.logger import logger
from src.bot import ScryfallBot

def main():
    logger.info("Starting Scryfall RPA Process")
    
    # Check if input file exists
    if not os.path.exists(config.INPUT_EXCEL_PATH):
        logger.error(f"Input file not found: {config.INPUT_EXCEL_PATH}")
        sys.exit(1)
        
    try:
        # Load input data
        df_input = pd.read_excel(config.INPUT_EXCEL_PATH)
        if "Card Name" not in df_input.columns:
            logger.error("Input Excel must contain a 'Card Name' column.")
            sys.exit(1)
            
        card_names = df_input["Card Name"].dropna().tolist()
        logger.info(f"Found {len(card_names)} cards to process.")
        
    except Exception as e:
        logger.error(f"Failed to read input Excel file: {e}")
        sys.exit(1)

    results = []
    bot = None
    try:
        bot = ScryfallBot(headless=True)
        
        for name in card_names:
            try:
                data = bot.search_card(name)
                if data:
                    results.append(data)
                else:
                    results.append({
                        "Searched Name": name,
                        "Found Name": "N/A",
                        "Set & Rarity": "N/A",
                        "Price USD": "N/A"
                    })
            except Exception as e:
                logger.error(f"Failed to process card '{name}': {e}")
                results.append({
                    "Searched Name": name,
                    "Found Name": "ERROR",
                    "Set & Rarity": "ERROR",
                    "Price USD": "ERROR"
                })
                
    except Exception as e:
        logger.error(f"Critical error during bot execution: {e}")
    finally:
        if bot:
            bot.close()

    # Save results
    if results:
        try:
            df_output = pd.DataFrame(results)
            os.makedirs(os.path.dirname(config.OUTPUT_EXCEL_PATH), exist_ok=True)
            df_output.to_excel(config.OUTPUT_EXCEL_PATH, index=False)
            logger.info(f"Successfully saved results to {config.OUTPUT_EXCEL_PATH}")
        except Exception as e:
            logger.error(f"Failed to save output Excel file: {e}")
    else:
        logger.warning("No results to save.")
        
    logger.info("Scryfall RPA Process finished.")

if __name__ == "__main__":
    main()
