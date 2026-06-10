ALTER TABLE projects 
ADD COLUMN mode TEXT NOT NULL DEFAULT 'novel' 
CHECK (mode IN ('novel', 'screenplay'));
 
-- Also add location as a valid category for bible_facts
ALTER TABLE bible_facts 
DROP CONSTRAINT IF EXISTS bible_facts_category_check;
 
ALTER TABLE bible_facts 
ADD CONSTRAINT bible_facts_category_check 
CHECK (category IN ('character', 'world', 'plot_thread', 'established_fact', 'location'));