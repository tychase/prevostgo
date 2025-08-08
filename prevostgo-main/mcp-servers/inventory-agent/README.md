# PrevostGo Inventory Agent MCP Server

An MCP server that provides comprehensive inventory management capabilities for the PrevostGo platform.

## Features

### Tools

#### Data Import & Scraping
- **run_scraper**: Run the Prevost inventory scraper to fetch latest coaches from prevost-stuff.com
- **add_coach**: Add a new coach to the inventory manually
- **bulk_import_csv**: Import multiple coaches from CSV file

#### Data Management
- **update_coach**: Update coach information (price, status, etc.)
- **check_duplicates**: Find potential duplicate listings
- **fix_data_issues**: Automatically fix common data problems (standardize names, fix prices)

#### Data Export
- **export_inventory**: Export inventory in CSV or JSON format

### Resources
- **inventory://database-stats**: Current database statistics and inventory health
- **inventory://scraper-status**: Last scraper run status
- **inventory://data-quality**: Data quality analysis report

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your paths
```

3. Build the server:
```bash
npm run build
```

4. Setup Claude Desktop (automatic):
```bash
npm run setup-claude
```

5. Restart Claude Desktop

## Usage Examples

### Run the Scraper
```
Run the scraper to get all coaches from prevost-stuff.com
Run the scraper with a limit of 50 coaches for testing
```

### Fix Data Issues
```
Fix data issues in the inventory
Show me what data issues can be fixed (dry run)
Standardize all converter names
```

### Check Data Quality
```
Show me the data quality report
Check for duplicate coaches
How many coaches are missing prices?
```

### Export Data
```
Export all coaches to CSV
Export available coaches with prices to JSON
Create a CSV with just id, title, price, and converter fields
```

### Update Coaches
```
Update coach [ID] to sold status
Change the price of coach [ID] to $450,000
```

## Common Tasks

### Initial Data Population
1. Run the scraper: "Run the inventory scraper"
2. Check results: "Show me database statistics"
3. Fix issues: "Fix data issues in dry run mode" then "Apply the fixes"

### Regular Maintenance
1. Daily scrape: "Run the scraper to check for new coaches"
2. Data quality: "Show me the data quality report"
3. Fix duplicates: "Check for duplicate coaches with 0.8 similarity"

### Data Export for Reports
1. Full export: "Export all available coaches to CSV"
2. Custom export: "Export coaches with specific fields to CSV"

## Integration with Search Agent

The inventory agent works seamlessly with the search agent:
- Inventory agent populates and maintains the data
- Search agent queries and retrieves the data
- Both use the same backend API

## Troubleshooting

### Scraper not working
- Check Python is installed: `python --version`
- Verify scraper path in .env
- Check backend is running on correct port

### Data quality issues
- Run "fix data issues" tool
- Check for duplicates regularly
- Verify converter and model standardization

### Export issues
- Ensure coaches have been loaded
- Check field names match database schema
- Verify backend API is accessible

## Architecture Notes

This MCP server provides:
- Direct scraper integration
- Data quality management
- Bulk operations support
- Export capabilities
- Database maintenance tools

Future enhancements:
- Image management
- Automated scheduling
- Historical price tracking
- Dealer management
