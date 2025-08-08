# PrevostGo Inventory Agent - Quick Start

## 🚀 Setup (3 minutes)

### Step 1: Install
```bash
cd mcp-servers/inventory-agent
npm install
```

### Step 2: Configure
```bash
copy .env.example .env
# Edit if needed (usually defaults work)
```

### Step 3: Build
```bash
npm run build
```

### Step 4: Add to Claude
```bash
npm run setup-claude
```

### Step 5: Restart Claude Desktop

## 🧪 First Run - Populate Your Database

In Claude Desktop, say:

1. **"Run the inventory scraper"**
   - This will fetch all coaches from prevost-stuff.com
   - Takes about 2-3 minutes

2. **"Show me the database statistics"**
   - See how many coaches were imported
   - Check data completeness

3. **"Fix data issues"**
   - Standardizes converter and model names
   - Fixes price formatting

## 📊 Daily Operations

### Morning Routine
```
1. "Run the scraper to check for new coaches"
2. "Show me the data quality report"
3. "Fix any data issues found"
```

### Data Management
```
- "Check for duplicate coaches"
- "Update coach ABC123 to sold"
- "Export available coaches to CSV"
```

### Troubleshooting Data
```
- "How many coaches are missing prices?"
- "Show coaches with Unknown converter"
- "Fix converter names in dry run mode"
```

## 🔧 Common Issues

### No coaches found
- Make sure backend is running
- Check scraper can access prevost-stuff.com
- Try with a limit: "Run scraper with limit 10"

### Data quality problems
- Use "fix data issues" regularly
- Check for duplicates weekly
- Monitor missing prices

### Can't export
- Ensure coaches are loaded first
- Check backend is accessible
- Try smaller exports first

## 💡 Pro Tips

1. **Initial Setup**: Run scraper → Fix data → Export baseline
2. **Regular Updates**: Daily scraper runs keep inventory fresh
3. **Quality Control**: Weekly duplicate checks prevent issues
4. **Backups**: Export to CSV before major changes

## 🎯 Next Steps

Once inventory is populated:
1. Use search agent to browse coaches
2. Set up automated daily scraping
3. Create custom export templates
4. Build inventory reports
