-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- CLEAN SLATE (Optional: Remove if you want to keep old data, but project-based schema is a major change)
DROP TABLE IF EXISTS public.results;
DROP TABLE IF EXISTS public.videos;
DROP TABLE IF EXISTS public.projects;
DROP TABLE IF EXISTS public.user_roles;

-- 1. Create 'projects' table
CREATE TABLE public.projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    owner_id UUID, -- Removed REFERENCES auth.users(id) for testing
    status TEXT DEFAULT 'CREATED' CHECK (status IN ('CREATED', 'UPLOADED', 'ANALYZING', 'DRAFT_READY', 'WAITING_APPROVAL', 'RENDERING', 'COMPLETED')),
    script TEXT,
    questions JSONB,
    is_paid BOOLEAN DEFAULT FALSE,
    draft_url TEXT, -- Added for PRD-MONETIZATION single output rule
    final_url TEXT, -- Added for PRD-MONETIZATION single output rule
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create 'videos' table (Clips)
CREATE TABLE public.videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    storage_path TEXT,
    duration FLOAT, -- Added for PRD-MONETIZATION upload limits
    status TEXT DEFAULT 'processing',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create 'results' table (Analysis results)
CREATE TABLE public.results (
    video_id UUID PRIMARY KEY REFERENCES public.videos(id) ON DELETE CASCADE,
    data JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create 'user_roles' table
CREATE TABLE public.user_roles (
    user_id UUID PRIMARY KEY, -- Removed REFERENCES auth.users(id) for testing
    role TEXT NOT NULL CHECK (role IN ('ADMIN', 'CREATOR', 'EDITOR')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Create 'jobs' table (Simple Queue)
CREATE TABLE public.jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('analyze', 'render')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    payload JSONB,
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Disable RLS for MVP testing
ALTER TABLE public.projects DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.videos DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.results DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs DISABLE ROW LEVEL SECURITY;

-- 7. Basic Policies (Explicitly allow all for MVP testing)
DROP POLICY IF EXISTS "Allow all for projects" ON public.projects;
CREATE POLICY "Allow all for projects" ON public.projects FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow all for videos" ON public.videos;
CREATE POLICY "Allow all for videos" ON public.videos FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow all for results" ON public.results;
CREATE POLICY "Allow all for results" ON public.results FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow all for user_roles" ON public.user_roles;
CREATE POLICY "Allow all for user_roles" ON public.user_roles FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow all for jobs" ON public.jobs;
CREATE POLICY "Allow all for jobs" ON public.jobs FOR ALL USING (true) WITH CHECK (true);

-- 7. Storage Instructions:
-- Go to 'Storage' in Supabase Dashboard.
-- Create a new bucket named 'videos'.
-- Make it 'Public' for MVP.
