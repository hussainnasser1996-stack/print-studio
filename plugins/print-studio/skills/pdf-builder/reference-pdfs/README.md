# Reference PDFs

Drop existing PDFs here that you want Claude to extract aesthetic direction from (palette, typography, layout density). The skill's "Reference-PDF mode" reads from this folder.

Examples of what to drop here:
- An FT or Economist article whose look you want to match
- A competitor's teaser whose visual treatment is good
- Your firm's own past deal documents (if you want continuity)
- A McKinsey / BCG / Bain insights PDF
- Any printed material whose typography or color discipline is worth replicating

## How it gets used

When the user picks "Reference-PDF mode" in step 0 of the skill, Claude:

1. Reads the PDF (page 1 is usually enough for palette + typography signals)
2. Extracts 4-8 dominant hex codes
3. Identifies display vs body typography (matches against open-source equivalents if proprietary)
4. Notes layout density and column structure
5. Locks the extracted values as CSS variables before writing any HTML

Add as many references as you want — name them descriptively (`ft-weekend-2024.pdf`, `acme-prior-teaser.pdf`).
