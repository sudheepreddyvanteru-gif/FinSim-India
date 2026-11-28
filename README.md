# FinSim India

FinSim India is an educational NSE/BSE market dashboard and personal portfolio tracker.

## Current quote-data behaviour

- The public website displays only quote records supplied by an authorised snapshot or imported from eligible historical CSV files.
- The automatic public snapshot workflow is designed for historical exchange data at least **31 calendar days old**. It is not a real-time or intraday feed.
- The snapshot builder collects NSE and BSE cash-equity records from their exchange bhavcopies and adds all available NSE historical index-report rows (including NIFTY 50) and the BSE SENSEX benchmark record.
- NSE symbols and BSE scrip codes are kept exchange-specific. The browser expands its searchable company directory from the verified snapshot.
- Derivatives, bonds, ETFs, commodities and every exchange index are not claimed to be included by this cash-equity workflow.
- No prices are fabricated when a data source is missing.

## Enable the public snapshot workflow

The workflow remains disabled until the repository owner has confirmed that the applicable exchange/data-provider terms and written public-display permissions cover this website and its educational use.

1. Review [MARKET_DATA_SETUP.md](MARKET_DATA_SETUP.md).
2. Confirm the relevant rights for both NSE and BSE with the data provider/exchange.
3. In GitHub, open **Settings → Secrets and variables → Actions → Variables**.
4. Add the repository variable `FINSIM_MARKET_DATA_AUTHORIZED` with value `true` only after the rights are confirmed.
5. Run **Actions → Update 31+ day delayed market data** once to test the pipeline.

The workflow publishes `data/market-quotes.json` to GitHub Pages after a complete snapshot passes validation. The site refreshes that archive on a configurable browser interval while open. GitHub Pages does not run a continuous backend process.

## Dashboard settings

The Settings page includes:
- Default exchange (NSE/BSE)
- Teal, ocean-blue or emerald accent
- Comfortable or compact layout
- Historical snapshot check interval
- Reduced-motion preference

Preferences are stored locally in the user's browser.

## Deployment

The frontend is a static GitHub Pages application. Open the repository's **Settings → Pages** to confirm the Pages source/branch and deployment status.

## Important

FinSim India is an educational information and portfolio-recording tool. It does not place, route or execute exchange orders and does not provide investment advice. Public market-data distribution must comply with the applicable exchange and provider agreements and regulations.
