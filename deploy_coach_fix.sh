#!/bin/bash

echo "Applying coach detail endpoint fix for Railway deployment..."

# Create a Python script to fix the issue
cat > backend/fix_coach_endpoint.py << 'EOF'
"""
Quick fix for the coach detail endpoint async issue
"""

import fileinput
import sys

# Read the inventory.py file and fix the get_coach endpoint
filename = "app/routers/inventory.py"

print(f"Fixing {filename}...")

# Flag to track if we're in the get_coach function
in_get_coach = False
fixed = False

lines = []
with open(filename, 'r') as f:
    lines = f.readlines()

# Find and replace the get_coach endpoint
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this is the start of get_coach
    if '@router.get("/{coach_id}")' in line and not fixed:
        # Replace the entire get_coach function with a fixed version
        new_lines.append(line)
        i += 1
        
        # Skip to the function definition
        while i < len(lines) and 'async def get_coach' not in lines[i]:
            new_lines.append(lines[i])
            i += 1
        
        # Now replace the function
        new_lines.append('''async def get_coach(
    coach_id: str,
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get single coach by ID"""
    try:
        # Use raw SQL for compatibility
        from sqlalchemy import text
        import json
        
        # Get coach data
        query = text("SELECT * FROM coaches WHERE id = :coach_id")
        result = await db.execute(query, {"coach_id": coach_id})
        coach_row = result.fetchone()
        
        if not coach_row:
            raise HTTPException(status_code=404, detail="Coach not found")
        
        # Update views
        await db.execute(
            text("UPDATE coaches SET views = COALESCE(views, 0) + 1 WHERE id = :coach_id"),
            {"coach_id": coach_id}
        )
        await db.commit()
        
        # Convert to dict
        coach_dict = dict(coach_row._mapping)
        
        # Parse JSON fields
        for field in ['images', 'features']:
            if isinstance(coach_dict.get(field), str):
                try:
                    coach_dict[field] = json.loads(coach_dict[field])
                except:
                    coach_dict[field] = []
        
        # Ensure lists
        coach_dict['images'] = coach_dict.get('images') or []
        coach_dict['features'] = coach_dict.get('features') or []
        
        # Convert price
        if coach_dict.get('price'):
            coach_dict['price'] = coach_dict['price'] // 100
            
        return coach_dict
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching coach {coach_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching coach details: {str(e)}")

''')
        
        # Skip the old function body
        brace_count = 0
        found_start = False
        while i < len(lines):
            if '{' in lines[i]:
                found_start = True
                brace_count += lines[i].count('{')
            if '}' in lines[i]:
                brace_count -= lines[i].count('}')
            
            # Check for the next function or route
            if (lines[i].strip().startswith('@') or 
                lines[i].strip().startswith('def ') or 
                lines[i].strip().startswith('async def ')) and found_start:
                break
                
            # Also check for common function end patterns
            if i + 1 < len(lines) and lines[i].strip() == '' and lines[i+1].strip() != '' and found_start:
                # Empty line followed by non-empty might be function end
                next_line = lines[i+1].strip()
                if (next_line.startswith('@') or 
                    next_line.startswith('def ') or 
                    next_line.startswith('async def ') or
                    next_line.startswith('#')):
                    break
            
            i += 1
        
        fixed = True
        continue
    
    new_lines.append(line)
    i += 1

# Write the fixed content
with open(filename, 'w') as f:
    f.writelines(new_lines)

print("Fix applied successfully!")
EOF

# Run the fix
cd backend && python fix_coach_endpoint.py

echo "Fix complete! Deploy to Railway with: railway up"