"""
Test CLIP embedding similarity scores to verify chromatographs are distinguishable
"""

import json
import numpy as np
from pathlib import Path

def cosine_similarity(emb1, emb2):
    """Calculate cosine similarity between two embeddings"""
    emb1 = np.array(emb1)
    emb2 = np.array(emb2)
    return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

def main():
    # Load embeddings
    project_root = Path(__file__).parent
    
    with open(project_root / 'data' / 'clip_embeddings_reference.json') as f:
        embeddings = json.load(f)
    
    print("="*70)
    print("🧪 Testing CLIP Embedding Similarity")
    print("="*70)
    print()
    
    # Group by disease category (from filename)
    hbe_images = [k for k in embeddings.keys() if 'hb_e_' in k.lower()]
    constant_spring = [k for k in embeddings.keys() if 'constant_spring' in k.lower()]
    d_zone = [k for k in embeddings.keys() if 'd_zone' in k.lower()]
    beta_thal = [k for k in embeddings.keys() if 'beta_thal' in k.lower()]
    
    print(f"📊 Dataset Overview:")
    print(f"   HbE images: {len(hbe_images)}")
    print(f"   Constant Spring: {len(constant_spring)}")
    print(f"   D Zone: {len(d_zone)}")
    print(f"   Beta Thalassemia: {len(beta_thal)}")
    print()
    
    # Test 1: Same disease (HbE vs HbE) - Should be HIGH
    print("="*70)
    print("🔬 Test 1: Same Disease (HbE vs HbE)")
    print("="*70)
    
    if len(hbe_images) >= 2:
        hbe_similarities = []
        for i in range(min(5, len(hbe_images))):
            for j in range(i+1, min(5, len(hbe_images))):
                sim = cosine_similarity(
                    embeddings[hbe_images[i]]['embedding'],
                    embeddings[hbe_images[j]]['embedding']
                )
                hbe_similarities.append(sim)
                print(f"   HbE #{i+1} ↔ HbE #{j+1}: {sim:.4f}")
        
        avg_same = np.mean(hbe_similarities)
        print(f"\n   Average similarity (same disease): {avg_same:.4f}")
        print(f"   Range: {min(hbe_similarities):.4f} - {max(hbe_similarities):.4f}")
    
    print()
    
    # Test 2: Different diseases - Should be LOWER
    print("="*70)
    print("🔬 Test 2: Different Diseases")
    print("="*70)
    
    different_tests = [
        ("HbE", hbe_images[:3], "Constant Spring", constant_spring[:3]),
        ("HbE", hbe_images[:3], "D Zone", d_zone[:3]),
        ("HbE", hbe_images[:3], "Beta Thal", beta_thal[:1]),
        ("Constant Spring", constant_spring[:2], "D Zone", d_zone[:2]),
    ]
    
    all_different = []
    
    for disease1, imgs1, disease2, imgs2 in different_tests:
        if not imgs1 or not imgs2:
            continue
        
        print(f"\n{disease1} vs {disease2}:")
        sims = []
        for img1 in imgs1:
            for img2 in imgs2:
                sim = cosine_similarity(
                    embeddings[img1]['embedding'],
                    embeddings[img2]['embedding']
                )
                sims.append(sim)
        
        avg_sim = np.mean(sims)
        print(f"   Average: {avg_sim:.4f}")
        print(f"   Range: {min(sims):.4f} - {max(sims):.4f}")
        all_different.extend(sims)
    
    print()
    
    # Test 3: Random pairs (baseline)
    print("="*70)
    print("🔬 Test 3: Random Pairs (Baseline)")
    print("="*70)
    
    import random
    all_images = list(embeddings.keys())
    random_pairs = []
    
    for _ in range(20):
        img1, img2 = random.sample(all_images, 2)
        sim = cosine_similarity(
            embeddings[img1]['embedding'],
            embeddings[img2]['embedding']
        )
        random_pairs.append(sim)
    
    avg_random = np.mean(random_pairs)
    print(f"   Average similarity (random): {avg_random:.4f}")
    print(f"   Range: {min(random_pairs):.4f} - {max(random_pairs):.4f}")
    print()
    
    # Summary
    print("="*70)
    print("📊 Summary & Analysis")
    print("="*70)
    print()
    
    if len(hbe_similarities) > 0 and len(all_different) > 0:
        avg_diff = np.mean(all_different)
        
        print(f"   Same Disease (HbE ↔ HbE):     {avg_same:.4f}")
        print(f"   Different Diseases:            {avg_diff:.4f}")
        print(f"   Random Pairs:                  {avg_random:.4f}")
        print()
        
        separation = avg_same - avg_diff
        print(f"   Separation Gap: {separation:.4f}")
        print()
        
        # Interpretation
        if separation > 0.15:
            print("   ✅ EXCELLENT: Strong separation between diseases!")
            print("   ✅ Cropped chromatographs are highly distinguishable")
            print("   ✅ Visual search will work well")
        elif separation > 0.08:
            print("   ✅ GOOD: Moderate separation between diseases")
            print("   ✅ Visual search should work reasonably well")
            print("   ⚠️  Some overlapping cases may occur")
        elif separation > 0.03:
            print("   ⚠️  WEAK: Small separation between diseases")
            print("   ⚠️  Visual search may have lower accuracy")
            print("   💡 Consider additional preprocessing or different crops")
        else:
            print("   ❌ POOR: No meaningful separation")
            print("   ❌ All chromatographs look too similar")
            print("   💡 Need to adjust cropping strategy")
    
    print()
    print("="*70)
    
    # Detailed breakdown
    if len(hbe_similarities) > 0:
        print()
        print("📈 Detailed Statistics:")
        print(f"   Same disease similarity:    {avg_same:.4f} ± {np.std(hbe_similarities):.4f}")
        if len(all_different) > 0:
            print(f"   Different disease similarity: {avg_diff:.4f} ± {np.std(all_different):.4f}")
        print(f"   Random baseline:             {avg_random:.4f} ± {np.std(random_pairs):.4f}")

if __name__ == "__main__":
    main()

