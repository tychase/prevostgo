# Patch Application Summary

## Applied Patches

### Backend Patches Applied ✅

1. **Created**: `backend/app/utils/normalize_specs.py`
   - Normalizes coach specifications from various dealer formats
   - Handles price parsing, slide count extraction, mileage normalization
   - Maps different field names to canonical ones

2. **Created**: `backend/migrations/20250807_add_spec_columns.sql`
   - SQL migration to add new columns to the listings table
   - Adds: model, chassis_type, mileage, slide_count, price, price_contact

### Frontend Patches Applied ✅

1. **Created**: `frontend/src/components/search/SearchBar.jsx`
   - New search bar component with Buy/Sell tabs
   - Debounced search with auto-search on filter changes
   - Sticky search button at bottom

2. **Created**: `frontend/src/components/listings/CoachCard.jsx`
   - New coach card component with normalized specs display
   - Shows model, chassis, mileage, slides in a clean format
   - Handles missing data gracefully with "—" placeholders

## Integration Steps Needed

### Backend Integration:

1. **Import and use normalize_specs in your scraper**:
   ```python
   from app.utils.normalize_specs import normalize_specs
   
   # In your scraper when processing coach data:
   normalized = normalize_specs(raw_specs_dict)
   coach.model = normalized['model']
   coach.chassis_type = normalized['chassis_type']
   # etc...
   ```

2. **Run the migration on your Railway database**:
   ```bash
   # Connect to Railway PostgreSQL and run:
   psql $DATABASE_URL < backend/migrations/20250807_add_spec_columns.sql
   ```

3. **Update your Coach model** in `backend/app/models/database.py`:
   ```python
   model = Column(String, nullable=True)
   chassis_type = Column(String, nullable=True)
   mileage = Column(Integer, nullable=True)
   slide_count = Column(Integer, nullable=True)
   price_contact = Column(Boolean, default=False)
   ```

### Frontend Integration:

1. **Use the new SearchBar component** in your HomePage or InventoryPage:
   ```jsx
   import SearchBar from '../components/search/SearchBar';
   
   const handleSearch = ({ mode, filters }) => {
     // Apply filters to your coach listing
     console.log('Search mode:', mode);
     console.log('Filters:', filters);
   };
   
   <SearchBar onSearch={handleSearch} />
   ```

2. **Replace your existing CoachCard** with the new one:
   ```jsx
   import CoachCard from '../components/listings/CoachCard';
   
   // Map your coach data to include specs:
   const coachWithSpecs = {
     ...coach,
     heroImageUrl: coach.images?.[0] || '/placeholder.jpg',
     specs: {
       model: coach.model,
       chassis_type: coach.chassis_type,
       mileage: coach.mileage,
       slide_count: coach.slide_count
     }
   };
   ```

## Git Commands to Push Changes:

```bash
# Add the new files
git add backend/app/utils/
git add backend/migrations/
git add frontend/src/components/search/
git add frontend/src/components/listings/

# Commit the changes
git commit -m "Add specs normalization and improved search/card components

- Add backend utils for normalizing coach specifications
- Add database migration for new spec columns
- Add new SearchBar component with buy/sell tabs
- Add improved CoachCard component with specs display"

# Push to GitHub
git push origin main
```

## Notes:
- The original patches were for TypeScript (.tsx) but I converted them to JavaScript (.jsx) to match your project
- The backend path was adjusted from `backend/src/` to `backend/app/` to match your structure
- You'll need to integrate these components into your existing pages and update your data flow