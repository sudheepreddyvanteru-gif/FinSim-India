# FinSim India — delayed market data setup

FinSim can load an automatically refreshed public snapshot containing NSE and BSE share closing prices, NSE index values (including NIFTY 50), SENSEX, and daily changes. The updater selects a common trading date at least **31 calendar days old**. It never generates simulated prices.

## Public data-sharing permission

The snapshot is published in this public GitHub Pages repository, so it redistributes exchange market-price data to website visitors. SEBI's circular dated 8 May 2026 allows educational/awareness sharing with a 30-day lag and without monetary incentives, and says the relevant exchange/intermediary must enter into an appropriate legal agreement with recipients. BSE also describes its daily EOD and historical market-data products as subscription products for datafeed customers.

Before enabling the workflow, the site owner must confirm that FinSim's use is covered by the relevant exchange/data-provider terms or written agreement for both NSE and BSE, including public website display. Do not enable it for a paid contest, prize, monetary reward, or other activity outside permitted educational use. This setup note is not legal advice.

## Enable after rights are confirmed

1. Open the FinSim India GitHub repository.
2. Go to **Settings → Secrets and variables → Actions → Variables**.
3. Add repository variable FINSIM_MARKET_DATA_AUTHORIZED with value true.
4. Go to **Actions → Update 31+ day delayed market data → Run workflow** for the first run.

No API key is required by this updater. The workflow is deliberately gated and remains skipped until that variable is set.

## Schedule and data

- Runs Monday to Friday at 14:30 UTC (about 8:00 PM India time).
- Uses a date at least 31 calendar days old and steps back over weekends, holidays, or missing reports.
- Downloads NSE/BSE cash-market equity bhavcopies and all available rows in the NSE historical index report (including NIFTY 50) and the BSE SENSEX historical index value. The builder requires at least 500 matched cash-equity securities from each exchange before publishing and keeps exchange-specific NSE symbols and BSE scrip codes.
- Generates data/market-quotes.json; the browser loads it after sign-in and checks for updates when the tab becomes active and every six hours while open.
- These are historical cash-equity closing prices, not live or intraday quotes. This workflow does not claim to cover derivatives, bonds, ETFs, commodities, or every NSE/BSE index. Additional instrument classes require separately licensed data sources and parsers.

If data-sharing rights are not confirmed, leave the variable unset. FinSim continues to support its existing manual CSV import, which stays in the user's browser.
