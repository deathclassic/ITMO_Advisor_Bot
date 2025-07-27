# Entry point for the bot
import pandas as pd
from parser.parse_ai import parse_ai_pdf_to_table
from parser.parse_ai_product import parse_ai_product_pdf_to_table
from parser.utils import save_to_csv, save_to_parquet

def main():
    df_ai = parse_ai_pdf_to_table()
    df_prod = parse_ai_product_pdf_to_table()

    if not df_ai.empty and not df_prod.empty:
        combined = pd.concat([df_ai, df_prod], ignore_index=True)
        save_to_csv(combined, "data/combined_curriculum.csv")
        save_to_parquet(combined, "data/combined_curriculum.parquet")

if __name__ == "__main__":
    main()

