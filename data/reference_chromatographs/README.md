# Reference Chromatographs Library

This folder contains reference chromatograph patterns organized by chromatography zones and pattern types.

## Folder Structure (17 Categories)

```
reference_chromatographs/
├── a0_shoulder_base/           # A0 peak with shoulder pattern
├── abnormal_a0/                # Abnormal A0 patterns
├── beta_thal_major/            # Beta thalassemia major patterns
├── broaden_a0/                 # Broadened A0 peak patterns
├── constant_spring/            # Hb Constant Spring patterns
├── d_zone/                     # D-Zone patterns
├── hb_e/                       # Hemoglobin E patterns
├── high_hbf/                   # High HbF patterns
├── hbhd/                       # HbH disease patterns
├── hb_q_thailand/              # Hb Q Thailand patterns
├── interference_substance/     # Interference substance patterns
├── s_window/                   # S-Window patterns
├── s_window_ce_silent/         # S-Window with CE silent patterns
├── small_not_variant/          # Small peaks (not variants)
├── z1/                         # Z1 zone patterns
├── z11/                        # Z11 zone patterns
└── z12/                        # Z12 zone patterns
```

---

## Classification System

Your references are organized by **chromatography zones and pattern characteristics** rather than disease names. This is more practical for pattern matching and analysis.

---

## Category Descriptions

### 1. **a0_shoulder_base/** 
A0 peak with shoulder pattern
- A0 peak showing shoulder-like appearance
- Secondary bump or widening adjacent to main A0 peak
- May indicate variant or heterogeneity

### 2. **abnormal_a0/**
Abnormal A0 patterns
- Atypical A0 peak shapes
- Deviations from normal A0

### 3. **beta_thal_major/**
Beta thalassemia major patterns
- High HbF patterns
- Characteristic beta thal major chromatographs

### 4. **broaden_a0/**
Broadened A0 peak patterns
- Wide A0 peaks
- May indicate heterogeneity

### 5. **constant_spring/**
Hb Constant Spring patterns
- Alpha chain variant
- Often associated with HbH disease

### 6. **d_zone/**
D-Zone patterns
- Patterns in the D retention time zone
- HbD and similar variants

### 7. **hb_e/**
Hemoglobin E patterns
- HbE trait and disease
- Co-migrates with HbA2 zone

### 8. **high_hbf/**
High HbF patterns
- Elevated fetal hemoglobin
- Various causes (HPFH, beta thal, etc.)

### 9. **hbhd/**
HbH disease patterns
- Fast-moving HbH peak
- Alpha thalassemia related

### 10. **hb_q_thailand/**
Hb Q Thailand patterns
- Regional variant
- Specific chromatograph characteristics

### 11. **interference_substance/**
Interference substance patterns
- Non-hemoglobin peaks
- Artifacts or interfering compounds

### 12. **s_window/**
S-Window patterns
- HbS and variants in S retention time zone
- Sickle cell related patterns

### 13. **s_window_ce_silent/**
S-Window with CE silent patterns
- S-window patterns that are silent on CE
- Require additional testing

### 14. **small_not_variant/**
Small peaks detected by CE but NOT true variants
- CE detected small peaks that appear suspicious
- Upon confirmation: NOT actual hemoglobin variants
- False positives, artifacts, or interfering substances
- Important for training system to avoid misdiagnosis
- Examples: degradation products, chemical interference, sample artifacts

### 15. **z1/**
Z1 zone patterns
- Patterns in Z1 retention time zone
- Specific chromatography zone

### 16. **z11/**
Z11 zone patterns
- Patterns in Z11 retention time zone
- Specific chromatography zone

### 17. **z12/**
Z12 zone patterns
- Patterns in Z12 retention time zone
- Specific chromatography zone

---

## File Organization Tips

### Naming Convention
Use descriptive names that include key identifying information:

```
✅ Good examples:
- a0_shoulder_typical_case_001.pdf
- hbe_trait_elevated_a2_zone.pdf
- s_window_hbs_40percent.pdf
- z1_zone_unknown_variant.pdf

❌ Avoid:
- image1.pdf
- scan.pdf
- chromatograph.pdf
```

### Multiple Cases in Same Category
If you have multiple examples:
```
hb_e/
├── hbe_trait_case1.pdf
├── hbe_trait_case2.pdf
├── hbe_disease_homozygous.pdf
└── hbe_beta_thal.pdf
```

---

## What to Document

For each reference PDF, consider creating a companion `.txt` file:

Example: `hb_e/hbe_trait_case1.txt`
```
Pattern: HbE trait
Peak positions: A0 zone ~60%, E zone ~30%
HbA2 zone: Elevated (includes HbE)
Retention times: HbE at 3.3 min (co-migrates with HbA2)
Clinical context: Asymptomatic patient, family history positive
Special notes: Requires DNA testing to confirm HbE vs elevated HbA2
```

---

## Usage in System

These references will be used for:

✅ **Pattern matching** - Compare unknown to known patterns  
✅ **Zone identification** - Identify which zone peaks appear in  
✅ **Visual library** - Show users similar reference cases  
✅ **AI training** - Teach vision model to recognize patterns  
✅ **Quality control** - Validate system accuracy  
✅ **Differential diagnosis** - Distinguish similar patterns  

---

## Pattern Matching Workflow

When user uploads a new chromatograph:

1. **Zone identification** → Identify which zones have peaks
2. **Reference lookup** → Find references in matching zones
3. **Pattern comparison** → Compare shape and retention times
4. **Top matches** → Return most similar reference patterns
5. **Diagnosis suggestion** → Provide likely diagnosis with confidence

---

## Next Steps

### Now:
✅ **Folders created** - 17 categories ready
✅ **PDFs organized** - You've placed them in folders

### Later (when coding):
⏳ **Extract images** - Pull chromatograph images from PDFs
⏳ **Generate metadata** - Create structured data for each reference
⏳ **Build search index** - Enable pattern-based search
⏳ **Integrate into UI** - Display reference gallery

---

## Special Notes

### Zone-Based Classification
Your classification system is more granular and technical than disease-based. This is excellent for:
- Precise pattern matching
- Handling ambiguous cases
- Identifying interference
- Teaching diagnostic reasoning

### Retention Time Zones
Make sure to document retention times for each category:
- A0 zone: typically 2.8-3.0 min
- A2/E zone: typically 3.2-3.4 min
- S-window: typically 4.0-4.5 min
- D-zone: variable by system
- Z zones: system-specific

### CE vs HPLC
If your references include both CE and HPLC:
- Note which method for each reference
- Different retention times expected
- Some patterns (S-window CE silent) specific to method

---

## Folder Status

✅ All 17 folders created and ready for your PDFs!

```
Current location:
/Users/jc/Desktop/hbpatterncheck/hbpatterncheck/data/reference_chromatographs/
```

---

## Quick Reference Table

| # | Folder | Pattern Type | Key Feature |
|---|--------|-------------|-------------|
| 1 | a0_shoulder_base | Pattern | A0 peak with shoulder |
| 2 | abnormal_a0 | Variant | Atypical A0 |
| 3 | beta_thal_major | Disease | High HbF |
| 4 | broaden_a0 | Pattern | Wide A0 peak |
| 5 | constant_spring | Variant | Alpha variant |
| 6 | d_zone | Zone | D-zone patterns |
| 7 | hb_e | Variant | A2-zone elevation |
| 8 | high_hbf | Elevated | High HbF various causes |
| 9 | hbhd | Disease | Fast HbH peak |
| 10 | hb_q_thailand | Variant | Regional variant |
| 11 | interference_substance | Artifact | Non-Hb peaks |
| 12 | s_window | Zone | HbS-related |
| 13 | s_window_ce_silent | Pattern | CE silent S-window |
| 14 | small_not_variant | False Positive | CE peaks, confirmed NOT variants |
| 15 | z1 | Zone | Z1 patterns |
| 16 | z11 | Zone | Z11 patterns |
| 17 | z12 | Zone | Z12 patterns |

---

**Your classification system is ready!** 🎯

Place your PDFs in the corresponding folders and they'll be ready for processing when you build the extraction scripts.
