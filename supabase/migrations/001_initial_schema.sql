-- Projects table
CREATE TABLE projects (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID,
  title TEXT NOT NULL,
  premise TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Scenes table with versioning
CREATE TABLE scenes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  scene_number INTEGER NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  content TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(project_id, scene_number, version)
);

-- Bible facts table - one row per atomic fact
CREATE TABLE bible_facts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  source_scene_id UUID REFERENCES scenes(id),
  category TEXT NOT NULL CHECK (category IN ('character', 'world', 'plot_thread', 'established_fact')),
  content JSONB NOT NULL,
  status TEXT NOT NULL DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'needs_review')),
  last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Bible questions - ambiguities surfaced by extraction
CREATE TABLE bible_questions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  source_scene_id UUID REFERENCES scenes(id),
  questions JSONB NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'resolved')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Embeddings table for vector search (Phase 2)
CREATE TABLE embeddings (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  scene_id UUID REFERENCES scenes(id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  chunk_text TEXT NOT NULL,
  embedding_vector vector(1536),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_bible_facts_project ON bible_facts(project_id);
CREATE INDEX idx_bible_facts_source ON bible_facts(source_scene_id);
CREATE INDEX idx_scenes_project ON scenes(project_id, scene_number);
